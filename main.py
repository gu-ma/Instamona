from instagram.utils import login
from instagram.utils import get_new_posts
from instagram.utils import extract_post_data
from instagram.utils import post_photo
from instagram.utils import post_video
from predict import predict
import cv2
import os
import logging
import argparse
from time import time, sleep, strptime
from datetime import datetime, date
from dateutil import relativedelta
from urllib import request

def str_to_dt(date_str):
    date = strptime(date_str, "%Y-%m-%d")
    date = datetime(*date[:6])
    return date

def load_last_date():
    last_runtime = open("instagram/last_runtime.txt", "r")
    timestamp = last_runtime.read()
    if timestamp:
        timestamp = float(timestamp)
        return datetime.utcfromtimestamp(timestamp)

def save_last_runtime(date):
    last_runtime = open("instagram/last_runtime.txt", "w") 
    file = str(date)
    last_runtime.write(file)
    last_runtime.close()

def main(args):
 
    # Define variables 
    config_path = 'yolo/config.json'
    weights_path = 'yolo/full_yolo_mona_03.h5'
    tag = 'monalisaselfie'

    # Login
    print('--------------------')
    print('[IG - LOGIN] \nusr:%s \npwd:%s' % (args.username, args.password))
    print('--------------------')
    api = login(args)

    # If a last runtime does not exist create it
    if not load_last_date():
        save_last_runtime(time())
    # Set the date interval for the IG search
    from_date = str_to_dt(args.from_time) if args.from_time else load_last_date()
    to_date = str_to_dt(args.to_time) if args.to_time else datetime.now()

    # Set default directories for images
    path_in = os.path.join(os.getcwd(), 'media', 'in')
    path_out = os.path.join(os.getcwd(), 'media', 'out')
    # Clean their contents
    tmp = [os.remove(os.path.join(path_in, f)) for f in os.listdir(path_in)]
    # tmp = [os.remove(os.path.join(path_out, f)) for f in os.listdir(path_out)]

    # Get new posts from IG
    print('--------------------')
    print('[IG - GET POSTS] \n#%s' % tag)
    print('from %s to %s' % (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
    print('--------------------')
    new_posts = get_new_posts(api, from_date, to_date, tag, args.username, args.media_type)
    posts = [extract_post_data(post) for post in new_posts]
    
    # # Parse and save new images / videos
    # for post in posts:
        
    #     thumb_ext = ''

    #     if post.video_url:
    #         video_fn = post.id + '.mp4'
    #         request.urlretrieve(post.video_url, os.path.join(path_in, video_fn))
    #         print("%s - %s \nSaved as %s" % (post.date, post.username, video_fn))
    #         thumb_ext = '_thumb'
        
    #     if post.image_url:
    #         image_fn = post.id + thumb_ext + '.jpg'
    #         request.urlretrieve(post.image_url, os.path.join(path_in, image_fn))
    #         print("%s - %s \nSaved as %s" % (post.date, post.username, image_fn))
        
    #     sleep(.5)

    # # Predict, process and save all photos containing Monalisa
    # print('--------------------')
    # print("[YOLO - PREDICTING]")
    # print('--------------------')
    # files_in = [f for f in os.listdir(path_in)]
    # predict(config_path, weights_path, files_in, path_in, path_out)

    # Post the resulting images
    print('--------------------')
    print('[IG - POST NEW PHOTOS]')
    print('usr:%s \npwd:%s' % (args.username, args.password))
    print('--------------------')
    fp_out = [os.path.join(path_out, f) for f in os.listdir(path_out)]

    for post in posts:
        paths = [fp for fp in fp_out if post.id in fp]

        for path in paths:

            basename, ext = os.path.splitext(path)
            
            caption = '@%s #%s' % (post.username, tag)
            print('%s %s %s' % (post.id, post.username, caption))

            if ext == '.jpg' and not '_thumb' in path:

                img = cv2.imread(path)
                w = img.shape[1]
                h = img.shape[0]
                img_str = cv2.imencode('.jpg', img)[1].tostring()
                
                if args.media_type == 0 or args.media_type == 1:
                    if not args.test:
                        post_photo(api, img_str, (w,h), caption)
                        print('%s posted on Instagram' % path)
                        sleep(10)

            if ext == '.mp4':

                video_reader = cv2.VideoCapture(path)
                nb_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
                w = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(video_reader.get(cv2.CAP_PROP_FPS))
                duration = nb_frames/fps

                video_file = open(path, 'r')
                print(basename + '_thumb.jpg')
                thumb = cv2.imread(basename + '_thumb.jpg')
                thumb_str = cv2.imencode('.jpg', thumb)[1].tostring()

                if args.media_type == 0 or args.media_type == 2:
                    if not args.test:
                        post_video(api, video_file, (w, h), duration, thumb_str, caption)
                        print('%s posted on Instagram' % path)
                        sleep(10)

    # Save the runtime
    if not args.test:
        save_last_runtime(time())

if __name__ == '__main__':

    # Logging settings
    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python main.py -u "ig_username" -p "ig_password" -settings "instagram/credentials.json" -f yyyy-mm-dd -t yyyy-mm-dd
    parser = argparse.ArgumentParser(description='main routine')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-f', '--from_time', dest='from_time', type=str, required=False, metavar="(YYYY-MM-DD)")
    parser.add_argument('-t', '--to_time', dest='to_time', type=str, required=False, metavar="(YYYY-MM-DD)")
    parser.add_argument('-dbg', '--debug', dest='debug', action='store_true')
    parser.add_argument('-tst', '--test', action='store_true')
    parser.add_argument('-mt', '--media_type', dest='media_type', type=int, default=0, help='media_type: 1=image, 2=Video, 8=Album, 0=All')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    main(args)
