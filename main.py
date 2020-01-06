import requests
import random
import os
from dotenv import load_dotenv

VK_API_PARAMS = dict(group_id=190509694)
FILENAME = 'comic.png'


def get_random_comic_num():
    xkcd_url = 'http://xkcd.com/info.0.json'
    response = requests.post(url=xkcd_url)
    response.raise_for_status()
    num_of_comics = response.json()['num']
    random_num = random.randint(0, num_of_comics)
    return random_num


def upload_image_and_comment(random_num=get_random_comic_num()):
    random_comic_url = 'http://xkcd.com/{}/info.0.json'.format(random_num)
    random_comic_response = requests.post(url=random_comic_url)
    random_comic_data = random_comic_response.json()
    comic_image = random_comic_data['img']
    comic_comment = random_comic_data['alt']
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
        'group_id': VK_API_PARAMS['group_id'],

    }
    vk_response = requests.get(url=url, params=params)
    vk_response.raise_for_status()
    wall_upload_server_answer = vk_response.json()
    VK_API_PARAMS['album_id'] = wall_upload_server_answer['response']['album_id']
    upload_url = wall_upload_server_answer['response']['upload_url']
    VK_API_PARAMS['user_id'] = wall_upload_server_answer['response']['user_id']
    with open(FILENAME, 'rb') as file:
        files = {
            'photo': file,
        }
        upload_file = requests.post(url=upload_url, files=files)
        upload_file.raise_for_status()
        upload_file_data = upload_file.json()
        VK_API_PARAMS['vk_photo'] = upload_file_data['photo']
        VK_API_PARAMS['vk_hash'] = upload_file_data['hash']
        VK_API_PARAMS['vk_server'] = upload_file_data['server']
    return VK_API_PARAMS


def save_wall_photo(vk_access_token):
    save_image_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    vk_params = {
        'access_token': vk_access_token,
        'v': 5.103,
        'user_id': 190509694,
        'group_id': 190509694,
        'photo': VK_API_PARAMS['vk_photo'],
        'server': VK_API_PARAMS['vk_server'],
        'hash': VK_API_PARAMS['vk_hash'],
        'caption': 'first comics today'
    }
    save_photo = requests.post(url=save_image_url, params=vk_params)
    save_photo.raise_for_status()
    save_wall_photo_answer = save_photo.json()
    VK_API_PARAMS['media_id'] = save_wall_photo_answer['response'][0]['id']
    VK_API_PARAMS['owner_page_id'] = save_wall_photo_answer['response'][0]['owner_id']
    return VK_API_PARAMS


def get_wall_post(vk_access_token, comic_comment=upload_image_and_comment()):
    vk_publish_url = 'https://api.vk.com/method/wall.post'
    attachments = 'photo' + str(VK_API_PARAMS['owner_page_id']) + '_' + str(VK_API_PARAMS['media_id'])
    params = {
        'access_token': vk_access_token,
        'owner_id': '-' + str(VK_API_PARAMS['group_id']),
        'from_group': 1,
        'attachments': attachments,
        'message': comic_comment,
        'v': 5.103,
    }
    vk_publish = requests.post(url=vk_publish_url, params=params)
    vk_publish.raise_for_status()


def main():
    load_dotenv()
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')

    get_random_comic_num()
    upload_image_and_comment()
    try:
        get_wall_upload_server(vk_access_token)
        get_wall_upload_server(vk_access_token)
        save_wall_photo(vk_access_token)
        get_wall_post(vk_access_token)
    finally:
        os.remove(FILENAME)


if __name__ == '__main__':
    main()
