from lib2to3.pgen2 import token
import requests
import os.path
import json

with open('access_token.txt', 'r') as file_object:
    token = file_object.read().strip()

class VkPhoto:
    def __init__(self, id, likes, date, size):
        self.id = id
        self.likes = likes
        self.date = date
        self.size = size


class VkUser:
    url_1 = 'https://api.vk.com/method/'
    url_2 = 'https://cloud-api.yandex.net/v1/disk/resources'
    yandex_folder = 'anton_naumov'
    photos = []
    photo_names = {}

    def __init__(self, vk_token, yandex_token):
        self.yandex_token = yandex_token
        self.vk_token = vk_token


    def get_photos(self, vk_id):
        """ Получение фотографии с профиля с использованием метода photos.get"""

        global_params = {
            'access_token': self.vk_token,
            'v': '5.131'
        }
        request_params = {
            'owner_id' : vk_id,
            'album_id' : 'profile',
            'rev' : 0,
            'extended' : 1,
            'photo_sizes' : 0,
            'count' : 20
        }

        resp = requests.get(self.url_1 + 'photos.get', params={**global_params, **request_params}).json()

        response_photos = resp['response']['items']
        self.photos = []

        for element in response_photos:
            largest_photo = (element['sizes'][-1])
            largest_photo_url = largest_photo['url']
            download_photo = requests.get(largest_photo_url)
            photo = VkPhoto(element['id'], element['likes']['count'], element['date'], largest_photo['type'])
            self.photos.append(photo)
            with open(os.path.join('fotos/', f'{photo.id}.jpg'), 'wb') as file:
                file.write(download_photo.content)


    def calculate_names(self):
        self.photo_names = {}
        for ph in self.photos:
            name = f'{ph.likes}.jpg'
            if name in self.photo_names:
                name = f'{ph.likes}_{ph.date}.jpg'
            self.photo_names[name] = ph

    def save_log(self):
        logs = []
        for name in self.photo_names:
            logs.append({'file_name': name, 'size': self.photo_names[name].size})

        with open('log.json', 'w') as file:
            json.dump(logs, file, indent=2)

    def get_yandex_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.yandex_token}'
        }

    def create_yandex_folder(self):
        '''Создание папки. path: Путь к создаваемой папке'''

        requests.put(f'{self.url_2}?path={self.yandex_folder}', headers=self.get_yandex_headers())

    def upload_photos(self):
        for name in self.photo_names:
            ph = self.photo_names[name]
            self.upload_file(f'{ph.id}.jpg', name)

    def upload_file(self, local_file, remote_file, replace=False):
        '''Загрузка файла.
        savefile: Путь к файлу на Диске
        loadfile: Путь к загружаемому файлу
        replace: true or false Замена файла на Диске'''

        res = requests.get(f'{self.url_2}/upload?path={self.yandex_folder}/{remote_file}&overwrite={replace}', headers=self.get_yandex_headers()).json()
        with open(f'fotos/{local_file}', 'rb') as f:
            try:
                file_upload = requests.put(res['href'], files={'file':f})
                status = file_upload.status_code
                if 500 > status != 400:
                    print('Фотографии успешно загружены!')
            except KeyError:
                print('Фотографии уже были загружены ранее')

def create_folder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
        return folder

def get_photos_from_folder(folder) -> list:
    file_list = os.listdir(folder)
    return file_list

if __name__ == '__main__':
    # создание папки внутри проекта
    new_folder = create_folder('fotos')
    token_yandex = input('токен с Полигона Яндекс.Диска: ')
    # создание экземпляра класса
    vk_client = VkUser(token, token_yandex)
    # вызов метода get_photos
    vk_client.get_photos(input('Введите id пользователя vk: '))
    vk_client.calculate_names()
    vk_client.save_log()
    vk_client.create_yandex_folder()
    vk_client.upload_photos()
