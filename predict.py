import argparse
import os
import cv2
import numpy as np
from tqdm import tqdm
from preprocessing import parse_annotation
from utils import draw_boxes
from frontend import YOLO
import json

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"

argparser = argparse.ArgumentParser(
    description='Train and validate YOLO_v2 model on any dataset')

argparser.add_argument(
    '-c',
    '--conf',
    help='path to configuration file')

argparser.add_argument(
    '-w',
    '--weights',
    help='path to pretrained weights')

argparser.add_argument(
    '-i',
    '--input',
    help='path to an image or an video (mp4 format)')


def predict(config_path, weights_path, filenames, path_in, path_out):

    with open(config_path) as config_buffer:
        config = json.load(config_buffer)

    ###############################
    #   Make the model 
    ###############################

    yolo = YOLO(architecture        = config['model']['architecture'],
                input_size          = config['model']['input_size'], 
                labels              = config['model']['labels'], 
                max_box_per_image   = config['model']['max_box_per_image'],
                anchors             = config['model']['anchors'])

    ###############################
    #   Load trained weights
    ###############################    

    print(weights_path)
    yolo.load_weights(weights_path)

    ###############################
    #   Predict bounding boxes 
    ###############################

    for filename in filenames:

        fp_in = os.path.join(path_in, filename)
        fp_out = os.path.join(path_out, filename)

        if fp_in[-4:] == '.mp4':

            video_reader = cv2.VideoCapture(fp_in)

            nb_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_h = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_w = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
            fps = int(video_reader.get(cv2.CAP_PROP_FPS))

            video_writer = cv2.VideoWriter(fp_out,
                                   cv2.VideoWriter_fourcc(*'mp4v'), 
                                   fps, 
                                   (frame_w, frame_h))
            boxes_count = 0
            for i in tqdm(range(nb_frames)):
                _, image = video_reader.read()
                
                boxes = yolo.predict(image)
                boxes_count += len(boxes)
                # image = draw_boxes(image, boxes, config['model']['labels'])
                image = draw_boxes(image, boxes, config['model']['labels'], 'pixelate', .025, .5)
                video_writer.write(np.uint8(image))

            acc = boxes_count/nb_frames
            print('%s average accuracy (boxes found per frame)' % acc )

            if (acc < .5):
                os.remove(fp_out)

            video_reader.release()
            video_writer.release() 

        else:

            image = cv2.imread(fp_in)
            boxes = yolo.predict(image)
            if len(boxes) > 0 or '_thumb' in filename:
                print('%s: %d boxes found ' % (filename, len(boxes)) )
                # good settings for cv2.INTER_CUBIC
                # img = draw_boxes(img, boxes, config['model']['labels'], 'pixelate', .04, .5)
                # good settings for cv2.INTER_LINEAR
                image = draw_boxes(image, boxes, config['model']['labels'], 'pixelate', .025, .5)
                # Save 
                cv2.imwrite(fp_out, image)
