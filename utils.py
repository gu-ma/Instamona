import numpy as np
import os
import xml.etree.ElementTree as ET
import tensorflow as tf
import copy
import cv2
import math

class BoundBox:
    def __init__(self, x, y, w, h, c = None, classes = None):
        self.x     = x
        self.y     = y
        self.w     = w
        self.h     = h
        
        self.c     = c
        self.classes = classes

        self.label = -1
        self.score = -1

    def get_label(self):
        if self.label == -1:
            self.label = np.argmax(self.classes)
        
        return self.label
    
    def get_score(self):
        if self.score == -1:
            self.score = self.classes[self.get_label()]
            
        return self.score

class WeightReader:
    def __init__(self, weight_file):
        self.offset = 4
        self.all_weights = np.fromfile(weight_file, dtype='float32')
        
    def read_bytes(self, size):
        self.offset = self.offset + size
        return self.all_weights[self.offset-size:self.offset]
    
    def reset(self):
        self.offset = 4

def normalize(image):
    image = image / 255.
    
    return image

def bbox_iou(box1, box2):
    x1_min  = box1.x - box1.w/2
    x1_max  = box1.x + box1.w/2
    y1_min  = box1.y - box1.h/2
    y1_max  = box1.y + box1.h/2
    
    x2_min  = box2.x - box2.w/2
    x2_max  = box2.x + box2.w/2
    y2_min  = box2.y - box2.h/2
    y2_max  = box2.y + box2.h/2
    
    intersect_w = interval_overlap([x1_min, x1_max], [x2_min, x2_max])
    intersect_h = interval_overlap([y1_min, y1_max], [y2_min, y2_max])
    
    intersect = intersect_w * intersect_h
    
    union = box1.w * box1.h + box2.w * box2.h - intersect
    
    return float(intersect) / union
    
def interval_overlap(interval_a, interval_b):
    x1, x2 = interval_a
    x3, x4 = interval_b

    if x3 < x1:
        if x4 < x1:
            return 0
        else:
            return min(x2,x4) - x1
    else:
        if x2 < x3:
            return 0
        else:
            return min(x2,x4) - x3  

# type: 'line', 'blur_grid', 'pixelate' ( add 'blur')
# grid_ratio: size of the grid in % of the image (for 'blur_grid' and 'pixelate')
# blur_amount: amount of blur relative to image size
def draw_boxes(image, boxes, labels, type, grid_ratio, blur_amount):
    
    result_image = image.copy()

    for box in boxes:

        image_w = image.shape[1]
        image_h = image.shape[0]

        xmin  = int((box.x - box.w/2) * image_w)
        xmax  = int((box.x + box.w/2) * image_w)
        ymin  = int((box.y - box.h/2) * image_h)
        ymax  = int((box.y + box.h/2) * image_h)

        xmin = np.clip(xmin, 0, image_w)
        xmax = np.clip(xmax, 0, image_w)
        ymin = np.clip(ymin, 0, image_h)
        ymax = np.clip(ymax, 0, image_h)

        box_w = xmax - xmin
        box_h = ymax - ymin

        if type == 'line':

            cv2.rectangle(result_image, (xmin,ymin), (xmax,ymax), (0, 255, 0), 3)
            cv2.putText(result_image, 
                        labels[box.get_label()] + ' ' + str(box.get_score()), 
                        (xmin, ymin - 13), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        1e-3 * image_h, 
                        (0, 255, 0), 2)

        elif type == 'blur_grid':

            grid_size = int(image_w * grid_ratio)

            t = int(image_w * blur_amount / 10)
            blur_size = (t - t%2) + 1

            xoffset = int((math.ceil(box_w / grid_size) * grid_size - box_w) / 2)
            yoffset = int((math.ceil(box_h / grid_size) * grid_size - box_h) / 2)

            xmin  -= xoffset
            xmax  -= xoffset
            ymin  -= xoffset
            ymax  -= xoffset

            for col in range(0, box_w, grid_size):
                for row in range(0, box_h, grid_size):
                    x = xmin + col
                    y = ymin + row
                    # print (str(x) + ' ' + str(x+grid_size) + ' / ' + str(y) + ' ' + str(y+grid_size))
                    # check if out of bound
                    oobx = x + grid_size > image_w or x < 0
                    ooby = y + grid_size > image_h or y < 0
                    if ( not oobx and not ooby ):
                        sub_image = image[y:y+grid_size, x:x+grid_size]
                        sub_image = cv2.GaussianBlur(sub_image,(blur_size, blur_size), 0)
                        result_image[y:y+sub_image.shape[0], x:x+sub_image.shape[1]] = sub_image

        elif type == 'pixelate':

            sub_image = image[ymin:ymax, xmin:xmax]
            sub_image = cv2.resize(sub_image, (math.ceil(box_w*grid_ratio), math.ceil(box_h*grid_ratio)), interpolation=cv2.INTER_LINEAR)
            sub_image = cv2.resize(sub_image, (box_w, box_h), interpolation=cv2.INTER_LINEAR)            
            result_image[ymin:ymin+box_h, xmin:xmin+box_w] = sub_image
            # Alternative method with seamlessClone (does not work: 'segmentation fault' error)
            # mask = np.zeros(sub_image.shape, sub_image.dtype)
            # center = (int(box.x*image_w), int(box.y*image_h))
            # result_image = cv2.seamlessClone(sub_image, result_image, mask, center, cv2.MIXED_CLONE)

        else :

            print('Unknown type. Use: \'line\', \'blur_grid\' or \'pixelate\'')
            break
        
    return result_image
        
def decode_netout(netout, obj_threshold, nms_threshold, anchors, nb_class):
    grid_h, grid_w, nb_box = netout.shape[:3]

    boxes = []
    
    # decode the output by the network
    netout[..., 4]  = sigmoid(netout[..., 4])
    netout[..., 5:] = netout[..., 4][..., np.newaxis] * softmax(netout[..., 5:])
    netout[..., 5:] *= netout[..., 5:] > obj_threshold
    
    for row in range(grid_h):
        for col in range(grid_w):
            for b in range(nb_box):
                # from 4th element onwards are confidence and class classes
                classes = netout[row,col,b,5:]
                
                if classes.any():
                    # first 4 elements are x, y, w, and h
                    x, y, w, h = netout[row,col,b,:4]

                    x = (col + sigmoid(x)) / grid_w # center position, unit: image width
                    y = (row + sigmoid(y)) / grid_h # center position, unit: image height
                    w = anchors[2 * b + 0] * np.exp(w) / grid_w # unit: image width
                    h = anchors[2 * b + 1] * np.exp(h) / grid_h # unit: image height
                    confidence = netout[row,col,b,4]
                    
                    box = BoundBox(x, y, w, h, confidence, classes)
                    
                    boxes.append(box)

    # suppress non-maximal boxes
    for c in range(nb_class):
        sorted_indices = list(reversed(np.argsort([box.classes[c] for box in boxes])))

        for i in range(len(sorted_indices)):
            index_i = sorted_indices[i]
            
            if boxes[index_i].classes[c] == 0: 
                continue
            else:
                for j in range(i+1, len(sorted_indices)):
                    index_j = sorted_indices[j]
                    
                    if bbox_iou(boxes[index_i], boxes[index_j]) >= nms_threshold:
                        boxes[index_j].classes[c] = 0
                        
    # remove the boxes which are less likely than a obj_threshold
    boxes = [box for box in boxes if box.get_score() > obj_threshold]
    
    return boxes

def sigmoid(x):
    return 1. / (1. + np.exp(-x))

def softmax(x, axis=-1, t=-100.):
    x = x - np.max(x)
    
    if np.min(x) < t:
        x = x/np.min(x)*t
        
    e_x = np.exp(x)
    
    return e_x / e_x.sum(axis, keepdims=True)
