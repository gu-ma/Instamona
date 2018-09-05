from collections import namedtuple

import json
import codecs
import datetime
import os.path

from instagram_private_api_extensions import media

try:
    from instagram_private_api import (
        Client, ClientError, ClientLoginError, MediaRatios,
        ClientCookieExpiredError, ClientLoginRequiredError, 
        __version__ as client_version)
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from instagram_private_api import (
        Client, ClientError, ClientLoginError, MediaRatios,
        ClientCookieExpiredError, ClientLoginRequiredError,
        __version__ as client_version)


def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object


def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))


def extract_post_data(post):
    mt = post['media_type']
    # dt = datetime.datetime.fromtimestamp(post['taken_at']).strftime('%Y-%m-%d %H:%M:%S')
    dt = datetime.datetime.utcfromtimestamp(post['taken_at'])
    usr = post['user']['username']
    # media_type: 1=image, 2=Video, 8=Album
    vurl = ''
    iurl = ''
    if 'video_versions' in post.keys():
        vurl = post['video_versions'][0]['url'] 
    if 'image_versions2' in post.keys():
        iurl = post['image_versions2']['candidates'][0]['url'] 
    id = post['id']
    Post = namedtuple('Post', ['media_type', 'date', 'username', 'image_url', 'video_url', 'id'])
    return Post(mt, dt, usr, iurl, vurl, id)


def get_new_posts(api, from_date, to_date, tag, username, media_type):
    # Call the api
    new_posts = []
    uuid = Client.generate_uuid()
    results = api.feed_tag(tag, uuid)
    loop = True
    date_flags = 0
    date_flags_thresold = 4
    assert len(results.get('items', [])) > 0

    while loop:
        posts = results.get('items', [])

        # iterate throught the results
        for post in posts:
            # retrieve post data
            mt, dt, usr, iurl, vurl, id = extract_post_data(post)
            # if the post is within the date range
            if (dt > from_date and dt < to_date and usr != username):
                if mt == media_type or media_type == 0:
                    new_posts.append(post)
            # count the wrong dates
            if dt < from_date:
                date_flags += 1
            if date_flags > date_flags_thresold:
                loop = False

        next_max_id = results.get('next_max_id')
        results = api.feed_tag(tag, uuid, max_id = next_max_id)
        assert len(results.get('items', [])) > 0

    return new_posts


def post_photo(api, filepath, caption):
    data, size = media.prepare_image(filepath, aspect_ratios=MediaRatios.standard)
    api.post_photo(data, size, caption)


def post_video(api, filepath, thumb_data, caption):
    data, size, duration, thumb = media.prepare_video(filepath, aspect_ratios=MediaRatios.reel, skip_reencoding=True, save_path='8_modified.mp4')
    api.post_video_story(data, size, duration, thumb)


def login(args):
    settings_file_path = args.settings_file_path
    username = args.username
    password = args.password
    print('Client version: {0!s}'.format(client_version))
    device_id = None
    try:

        settings_file = settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(settings_file))
            print('New login...')

            # login new
            api = Client(
                username, password,
                on_login=lambda x: onlogin_callback(x, settings_file_path))
        else:
            with open(settings_file) as file_data:
                cached_settings = json.load(file_data, object_hook=from_json)
            print('Reusing settings: {0!s}'.format(settings_file))

            device_id = cached_settings.get('device_id')
            # reuse auth settings
            api = Client(
                username, password,
                settings=cached_settings)

    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))
        print('New login using default ua, keys etc...')

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            username, password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, settings_file_path))

    except ClientLoginError as e:
        print('ClientLoginError {0!s}'.format(e))
        exit(9)
    except ClientError as e:
        print('ClientError {0!s} (Code: {1:d}, Response: {2!s})'.format(e.msg, e.code, e.error_response))
        exit(9)
    except Exception as e:
        print('Unexpected Exception: {0!s}'.format(e))
        exit(99)

    # Show when login expires
    cookie_expiry = api.cookie_jar.expires_earliest
    print('Cookie Expiry date: {0!s}'.format(datetime.datetime.fromtimestamp(cookie_expiry).strftime('%Y-%m-%dT%H:%M:%SZ')))

    return api