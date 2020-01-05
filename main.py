import requests
import random
import os
from dotenv import load_dotenv

vk_dict = dict(group_id=190509694)
FILENAME = 'comic.png'


def get_random_num():
    xkcd_url = 'http://xkcd.com/info.0.json'
    response = requests.post(url=xkcd_url)
    response.raise_for_status()
    num_of_comics = response.json()['num']
    random_num = random.randint(0, num_of_comics)
    return random_num


def upload_image_and_comment(random_num=get_random_num()):
    random_comic_url = 'http://xkcd.com/{}/info.0.json'.format(random_num)
    random_comic_response = requests.post(url=random_comic_url)
    comic_image = random_comic_response.json()['img']
    comic_comment = random_comic_response.json()['alt']
    comic_upload_image = requests.get(url=comic_image)
    comic_upload_image.raise_for_status()
    with open(FILENAME, 'wb') as file:
        file.write(comic_upload_image.content)
    return comic_comment


def get_wall_upload_server(vk_access_token):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'access_token': vk_access_token,
        'v': 5.103,
        'group_id': vk_dict['group_id'],

    }
    vk_response = requests.get(url=url, params=params)
    vk_response.raise_for_status()
    vk_dict['album_id'] = vk_response.json()['response']['album_id']
    upload_url = vk_response.json()['response']['upload_url']
    vk_dict['user_id'] = vk_response.json()['response']['user_id']
    with open(FILENAME, 'rb') as file:
        files = {
            'photo': file,
        }
        upload_file = requests.post(url=upload_url, files=files)
        upload_file.raise_for_status()
        vk_dict['vk_photo'] = upload_file.json()['photo']
        vk_dict['vk_hash'] = upload_file.json()['hash']
        vk_dict['vk_server'] = upload_file.json()['server']
    return vk_dict


def save_wall_photo(vk_access_token):
    save_image_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    vk_params = {
        'access_token': vk_access_token,
        'v': 5.103,
        'user_id': 190509694,
        'group_id': 190509694,
        'photo': vk_dict['vk_photo'],
        'server': vk_dict['vk_server'],
        'hash': vk_dict['vk_hash'],
        'caption': 'first comics today'
    }
    save_photo = requests.post(url=save_image_url, params=vk_params)
    save_photo.raise_for_status()
    vk_dict['media_id'] = save_photo.json()['response'][0]['id']
    vk_dict['owner_page_id'] = save_photo.json()['response'][0]['owner_id']
    return vk_dict


def get_wall_post(vk_access_token, comic_comment=upload_image_and_comment()):
    vk_publish_url = 'https://api.vk.com/method/wall.post'
    attachments = 'photo' + str(vk_dict['owner_page_id']) + '_' + str(vk_dict['media_id'])
    params = {
        'access_token': vk_access_token,
        'owner_id': '-' + str(vk_dict['group_id']),
        'from_group': 1,
        'attachments': attachments,
        'message': comic_comment,
        'v': 5.103,
    }
    vk_publish = requests.post(url=vk_publish_url, params=params)
    vk_publish.raise_for_status()


def main():
    load_dotenv()
    vk_access_token = os.getenv('FB_ACCESS_TOKEN')

    get_random_num()
    upload_image_and_comment()
    get_wall_upload_server(vk_access_token)
    save_wall_photo(vk_access_token)
    get_wall_post(vk_access_token)
    os.remove(FILENAME)


if __name__ == '__main__':
    main()
