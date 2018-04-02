# Instagram project - InstaMona
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/webslides/webslides.svg?style=social)](https://twitter.com/g_massol)

Object detection on Instagram using Keras and Yolo. 

```python main.py -u "ig_usernamea" -p "ig_password" -settings "instagram/credentials.json" -f yyyy-mm-dd -t yyyy-mm-dd```

NB: the function to search time interval does not work properly, sometimes there are unsorted dates in the list returned by ```Instagram Private API```

> ![Mona Lova](https://raw.githubusercontent.com/gu-ma/Instamona/master/images/example.jpg)<br>
> <a href="https://www.instagram.com/p/BhDIvrrFp7e/" target="_blank">A post shared by Mona Lova (@m.o.n.a.l.o.v.a)</a> on Apr 1, 2018 at 6:06pm PDT

1) Search instagram for posts tagged _#Monalisaselfies_ <br>
2) Detect and blur the painting <br>
3) Post edited photo to Instagram <br>
4) Tag original uploader and add hashtag <br>

## Usage

### 0. Prepare your dataset

Prepare your dataset in the Pascal VOC format. I've used [labelImg](https://github.com/tzutalin/labelImg) as suggested in this [excellent post](https://towardsdatascience.com/how-to-train-your-own-object-detector-with-tensorflows-object-detector-api-bec72ecfe1d9). You can download a copy of the dataset I've used here

### 1. Train a model

Just follow the instructions from [Basic Yolo Keras](https://github.com/experiencor/basic-yolo-keras) to train your model (I've tested only with Full Yolo)

### 2. Create an instagram account

This can be done in the browser, just signup for a new user.

### 3. Copy weights from Basic Yolo Keras

Copy the frontend weights in the root folder and your trained weights + ```config.json``` in the ```yolo``` folder. 

### 4. Adjust variables

In ```main.py``` modify ```config_path``` and ```weights_path``` to match your weights name. Type your hashtag in ```tag```. **Set ```test_run``` to False to post the result images on IG.**

## Requirements:

See requirements from:

+ [Basic Yolo Keras](https://github.com/experiencor/basic-yolo-keras) which is used for training the model (Full YOLO)
+ [Instagram Private API](https://github.com/ping/instagram_private_api) used for searching hashtags, posting and tagging

NB: Most of the frontend code for predicting MonaLisa's location is taken from [Basic Yolo Keras](https://github.com/experiencor/basic-yolo-keras).

## Possible improvements
- [ ] Handle instagram videos
- [ ] Add weights_path, config_path, tag, simulate (run the program without posting on IG), simulated runtime, blur_type and blur_amount as args
- [ ] Add comments + simple doc :pencil:
- [ ] Keep a local record of posts (liteSQL)