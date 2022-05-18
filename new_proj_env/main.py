from lib2to3.pgen2 import token
import requests
import os.path
import json

with open('access_token.txt', 'r') as file_object:
    token = file_object.read().strip()

class VkUser:
    url_1 = 'https://api.vk.com/method/'
    url_2 = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token, version, token_yandex):
        self.token = token_yandex
        self.params = {
            'access_token': token,
            'v': version     
        }

    def get_photos(self, vk_id):
        ''' Получение фотографии с профиля с использованием метода photos.get'''
        photos_get_url = self.url_1 + 'photos.get'

        params = {
            'owner_id' : vk_id,
            'album_id' : 'profile',
            'rev' : 0,
            'extended' : 1,
            'photo_sizes' : 0,
            'count' : 20
        }
        res = requests.get(photos_get_url, params={**self.params, **params}).json()
        profile_list = res['response']['items']
        logs_list = []
        for element in profile_list:
            dictionary = (element['sizes'][-1])
            photo_url = (dictionary['url'])
            file_name = element['likes']['count']
            download_photo = requests.get(photo_url)
            download_log = {'file_name': f'{file_name}.jpg', 'size': dictionary['type']}
            logs_list.append(download_log)
            with open(os.path.join('fotos/', f'{file_name}.jpg'), 'wb') as file:
                file.write(download_photo.content)

        # Сохранение информации по фотографиям в json-файл с результатами
        with open('log.json', 'w') as file:
            json.dump(logs_list, file, indent=2)

        return 'Фотографии успешно сохранены!'

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        } 

    def create_folder(self, path):
        '''Создание папки. path: Путь к создаваемой папке'''

        requests.put(f'{self.url_2}?path={path}', headers=self.get_headers())

    def upload_file(self, loadfile, savefile, replace=False):
        '''Загрузка файла.
        savefile: Путь к файлу на Диске
        loadfile: Путь к загружаемому файлу
        replace: true or false Замена файла на Диске'''

        res = requests.get(f'{self.url_2}/upload?path={savefile}&overwrite={replace}', headers=self.get_headers()).json()
        with open(loadfile, 'rb') as f:
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
    vk_client = VkUser(token, '5.131', token_yandex)
    # вызов метода get_photos
    print(vk_client.get_photos(input('Введите id пользователя vk: ')))
    file_list = get_photos_from_folder('fotos')
    # вызов метода для создание папки на Яндес диске
    new_folder_disk = vk_client.create_folder('fotos')
    for file in file_list:
        vk_client.upload_file(f'fotos/{file}', f'fotos/{file}')
