import requests
import json

import re

#session = requests.Session()
#session.verify = False

# api-endpoint
# Страница сайта - https://iacpaas.dvo.ru/
# Адрес сервиса - https://iacpaas.dvo.ru/api/service/run/{id}
# Импорт (create) POST - https://iacpaas.dvo.ru/api/data/import
# Экспорт (read) GET - https://iacpaas.dvo.ru/api/data/export/user-item
# Обновление вершины (update) PUT - https://iacpaas.dvo.ru/api/data/update
# Удаление вершины (delete) DELETE - https://iacpaas.dvo.ru/api/data/delete

# авторизация в системе, возвращает JWT токен
def signin(username, password):
    URL = 'https://iacpaas.dvo.ru/api/signin'
    headers = {'Content-Type': 'application/json'}
    params = {'username': username, 'password': password}
    r = requests.post(url = URL, json = params, headers=headers)
    data = r.json()
    key = data.get('accessToken')
    return key

# выход из системы
def signout():
    URL = 'https://iacpaas.dvo.ru/api/signout'
    r = requests.post(url = URL)

'''
Возвращает строку с JSON с данными ресурса
Параметры:
API_KEY - X-API-KEY, выданный администратором ключ для авторизации
path - путь до EX в "Мой Фонд", откуда экспортируется JSON
json_type - "universal" или "meta" или "simple"
start_target_concept_path (необязательный) - путь до вершины, начиная с которой нужно экспортировать подграф
export_depth (необязательный) - глубина экспорта (0 - экспортировать только одну вершину - корень или указанную в качестве начальной)
compress (необязательный) - указание на необходимость (zip) сжатия результата (true/false)
no_blob_data (необязательный) - указание на необходимость пропускать в инфоресурсе blob-значения (true/false)
'''
# В случае успеха вернет словарь с ключами filename, code и data
def export_resource(API_KEY, path, json_type='universal', start_target_concept_path=None, export_depth=None, compress=None, no_blob_data=None):
    key = API_KEY
    URL = "https://iacpaas.dvo.ru/api/data/export/user-item"
    headers = {"Authorization": f"Bearer {key}", 'Content-Type': 'application/json'}
    #'X-API-KEY': API_KEY
    params = {'path': path, 'json-type': json_type}
    if start_target_concept_path is not None:
        params['start_target_concept_path'] = start_target_concept_path

    if export_depth is not None:
        params['export_depth'] = export_depth

    if compress is not None:
        params['compress'] = compress

    if no_blob_data is not None:
        params['no-blob-data'] = no_blob_data

    r = requests.get(url = URL, params = params, headers=headers)
    data = r.json()

    return data

'''
path - путь в "Мой Фонд" до папки, содержащей импортируемую EX (указывать в начале пути "<e-mail>>/Мой Фонд/" не нужно, также не нужно включать имя ЕХ, так как это путь к папке-контейнеру)
json - собственно импортируемый JSON в виде строки
clearIfExists - указание на необходимость очистки ИР (удаление всех вершин кроме корневой) перед импортом (true/false)
(clearIfExists проще всегда вносить со значением True, с полным удалением уже существующих данных)
'''
def import_resource(API_KEY, path, json, clearIfExists=True):
    key = API_KEY
    URL = 'https://iacpaas.dvo.ru/api/data/import'
    headers = {"Authorization": f"Bearer {key}", 'Content-Type': 'application/json'}
    params = {'path': path, 'json': json, 'clearIfExists': clearIfExists}

    r = requests.post(url = URL, json = params, headers = headers, timeout=120)

    data = r.json()
    return data
