# Instagram project - InstaMona
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![Twitter](https://img.shields.io/twitter/url/https/github.com/webslides/webslides.svg?style=social)](https://twitter.com/g_massol)

Object detection on Instagram using Keras and Yolo.

<blockquote class="instagram-media" data-instgrm-permalink="https://www.instagram.com/p/BhDIvrrFp7e/" data-instgrm-version="8" style=" background:#FFF; border:0; border-radius:3px; box-shadow:0 0 1px 0 rgba(0,0,0,0.5),0 1px 10px 0 rgba(0,0,0,0.15); margin: 1px; max-width:658px; padding:0; width:99.375%; width:-webkit-calc(100% - 2px); width:calc(100% - 2px);"><div style="padding:8px;"> <div style=" background:#F8F8F8; line-height:0; margin-top:40px; padding:36.06481481481482% 0; text-align:center; width:100%;"> <div style=" background:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAsCAMAAAApWqozAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAMUExURczMzPf399fX1+bm5mzY9AMAAADiSURBVDjLvZXbEsMgCES5/P8/t9FuRVCRmU73JWlzosgSIIZURCjo/ad+EQJJB4Hv8BFt+IDpQoCx1wjOSBFhh2XssxEIYn3ulI/6MNReE07UIWJEv8UEOWDS88LY97kqyTliJKKtuYBbruAyVh5wOHiXmpi5we58Ek028czwyuQdLKPG1Bkb4NnM+VeAnfHqn1k4+GPT6uGQcvu2h2OVuIf/gWUFyy8OWEpdyZSa3aVCqpVoVvzZZ2VTnn2wU8qzVjDDetO90GSy9mVLqtgYSy231MxrY6I2gGqjrTY0L8fxCxfCBbhWrsYYAAAAAElFTkSuQmCC); display:block; height:44px; margin:0 auto -44px; position:relative; top:-22px; width:44px;"></div></div><p style=" color:#c9c8cd; font-family:Arial,sans-serif; font-size:14px; line-height:17px; margin-bottom:0; margin-top:8px; overflow:hidden; padding:8px 0 7px; text-align:center; text-overflow:ellipsis; white-space:nowrap;"><a href="https://www.instagram.com/p/BhDIvrrFp7e/" style=" color:#c9c8cd; font-family:Arial,sans-serif; font-size:14px; font-style:normal; font-weight:normal; line-height:17px; text-decoration:none;" target="_blank">A post shared by Mona Lova (@m.o.n.a.l.o.v.a)</a> on <time style=" font-family:Arial,sans-serif; font-size:14px; line-height:17px;" datetime="2018-04-02T01:06:23+00:00">Apr 1, 2018 at 6:06pm PDT</time></p></div></blockquote> <script async defer src="//www.instagram.com/embed.js"></script>

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

## Possible improvments
- [ ] Handle instagram videos
- [ ] Add weights_path, config_path, tag, simulate (run the program without posting on IG), simulated runtime, blur_type and blur_amount as args
- [ ] Add comments + simple doc :pencil:
- [ ] Keep a local record of posts (liteSQL)