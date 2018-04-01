from instagram.utils import login, get_new_posts, extract_post_data, post_photos
from predict import predict
import cv2
import os
import logging
import argparse
from time import time, sleep
from datetime import datetime, date
from dateutil import relativedelta
from urllib import request


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
    weights_path = 'yolo/full_yolo_mona_01.h5'
    tag = 'monalisaselfie'
    test_run = True

    # Login
    api = login(args)

    # Load the last known runtime
    if (args.force_runtime):
        last_runtime = datetime.now() - relativedelta.relativedelta(months=int(args.force_runtime))
    else:
        last_runtime = load_last_date()
        if not last_runtime:
            save_last_runtime(time())
            last_runtime = time()

    # Set default directories for images
    img_path_in = os.path.join(os.getcwd(), 'images', 'in')
    img_path_out = os.path.join(os.getcwd(), 'images', 'out')
    # Clean their content
    tmp = [os.remove(os.path.join(img_path_in, f)) for f in os.listdir(img_path_in) if f.endswith("jpg")]
    tmp = [os.remove(os.path.join(img_path_out, f)) for f in os.listdir(img_path_out) if f.endswith("jpg")]

    # Get new posts from IG
    img_filenames = []
    posts_data = [extract_post_data(post) for post in get_new_posts(api, last_runtime, tag)]
    # Parse and save all new images
    for d in posts_data:
        request.urlretrieve(d.img_url, os.path.join(img_path_in, "%s.jpg" % d.id))
        print("%s - %s \nSaved as %s.jpg" % (d.date, d.username, d.id))
        img_filenames.append("%s.jpg" % d.id)
        sleep(.5)

    # Predict, process and save all photos containing Monalisa
    predict(config_path, weights_path, img_filenames, img_path_in, img_path_out)

    # Post the resulting images
    for d in posts_data:
        fp = os.path.join(img_path_out, "%s.jpg" % d.id)
        if os.path.isfile(fp):
            img = cv2.imread(fp)
            if img is not None:
                w = img.shape[1]
                h = img.shape[0]
                img_str = cv2.imencode('.jpg', img)[1].tostring()
                # tag user and add hashtag
                caption = '@%s #%s' % (d.username, tag)
                print('%s %s %s \n%s posted on Instagram' % (d.id, d.username, caption, fp))
                if not test_run:
                    post_photos(api, img_str, (w,h), caption)
                    sleep(5)

    # Save the runtime
    save_last_runtime(time())

if __name__ == '__main__':

    # Logging settings
    logging.basicConfig()
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)

    # Example command:
    # python main.py -u "yyy" -p "zzz" -settings "test_credentials.json"
    parser = argparse.ArgumentParser(description='main routine')
    parser.add_argument('-settings', '--settings', dest='settings_file_path', type=str, required=True)
    parser.add_argument('-u', '--username', dest='username', type=str, required=True)
    parser.add_argument('-p', '--password', dest='password', type=str, required=True)
    parser.add_argument('-fr', '--force-runtime', dest='force_runtime', type=str, required=False)    
    parser.add_argument('-debug', '--debug', action='store_true')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    main(args)
