from typing import List, Dict

import requests
import os
import json
import time
from abc import ABC, abstractmethod


class GetAPIDataError(Exception):

    def __init__(self):
        self.message = "GetAPIDataError: Ошибка получения данных от API"

    def __str__(self):
        return self.message


class GetAPIAbstractClass(ABC):

    @abstractmethod
    def get_api_data(self, vacation_name):
        """
        Абстрактный метод запроса к api платформы
        :param vacation_name: Название вакансии для поиска
        :return: None
        """
        pass

    @abstractmethod
    def get_api_vacancy_json_list(self):
        """
        Абстрактный метод для конвертации данных полученных от API
        в формат json
        :return: list json
        """
        pass


# Дочерний класс от GetAPIAbstractClass - HeadHunterAPI
class HeadHunterAPI(GetAPIAbstractClass):

    # Инициализация класса
    def __init__(self):
        self.__api_data = ''
        self.required_vacation = ''
        self.area = 113

    # Переопределение метода str, выводим имя родительского класса и запрос пользователя
    def __str__(self):
        return f"{HeadHunterAPI.__name__} считаны данные по запросу: {self.required_vacation}"

    def get_api_data(self, vacation_name: str) -> None:
        """
        Получение данных с сайта HH по API с запросом
        по вакансии - vacation_name, считываем максимальное
        количество страниц и собираем их в список json_data_list
        :param vacation_name: запрос пользователя (str)
        """
        self.required_vacation = vacation_name
        json_data_list = []
        try:
            for pages in range(0, 20):  # Читаем в цикле все страницы данных по вакансиям
                params = {
                    'text': vacation_name,
                    'host': 'hh.ru',
                    'locale': 'RU',
                    'area': self.area,
                    'page': pages,
                    'per_page': 100
                }
                recs = requests.get("https://api.hh.ru/vacancies", params)  # Запрос к API
                if recs.status_code != 200:
                    raise GetAPIDataError
                json_record = json.loads(recs.content.decode())    # Приводим полученные данные к формату json
                json_data_list.extend(json_record['items'])    # Добавляем данные каждой страницы в общий список
                if (json_record['pages'] - pages) <= 1:  # Если страниц меньше 20, дочитываем последнюю и прерываем цикл
                    break
                print(f'Загрузка страницы - {pages}')
                time.sleep(0.20)    # Задержка на запрос, чтобы не загружать сервер HH
        except GetAPIDataError:
            print(GetAPIDataError())
        self.__api_data = json_data_list

    def get_api_vacancy_json_list(self) -> list:
        """
        Метод для конвертации данных полученных от API HH
        Приведение формата полученных данных к единому стандарту
        :return:
        """
        vacation_list = []
        vacancy_counter = 0     # счетчик вакансий для вывода

        if self.__api_data is not None:     # Проверка, если есть данные, создаем список json для дальнейшей работы
            for data in self.__api_data:
                vacation_list.append(dict(id=data['id'], name=data['name'], url=data['url']))
                if data['salary'] is None:      # Подготовка данных по з\п, если данных нет - заполоняем
                    vacation_list[-1]['salary_from'] = '0'
                    vacation_list[-1]['salary_to'] = '0'
                else:
                    if data['salary']['from'] is None:
                        vacation_list[-1]['salary_from'] = '0'
                    else:
                        vacation_list[-1]['salary_from'] = str(data['salary']['from'])
                    if data['salary']['to'] is None:
                        vacation_list[-1]['salary_to'] = '0'
                    else:
                        vacation_list[-1]['salary_to'] = str(data['salary']['to'])
                if data['snippet']['requirement'] is None:
                    vacation_list[-1]['description'] = ''
                else:
                    vacation_list[-1]['description'] = data['snippet']['requirement']

                vacation_list[-1]['company'] = data['employer']['name']
                vacation_list[-1]['api'] = 'hh.ru'
                vacancy_counter += 1
        else:
            print('Нет данных от HeadHunter API')
        print(f'Загружено {vacancy_counter} вакансий с HeadHunter.ru')
        return vacation_list

    def find_area_id(self, area='') -> None:
        """
        Дополнительная функция для получения библиотеки городов с HH.ru
        и поиска ID города
        :param area: Название города -> str
        :return: None
        """
        try:
            rec = requests.get("https://api.hh.ru/areas/113")  # Запрашиваем словарь городов/областей
            if rec.status_code != 200:
                raise GetAPIDataError
            json_data = json.loads(rec.content.decode())
            if area not in ('', 'Россия'):
                my_str: str = area

                for i in json_data['areas']:     # Обход дерева регионов, поиск и вывод ID по названию города
                    if i['name'] == str(my_str):
                        self.area = i['id']
                        break
                    for y in i['areas']:
                        if y['name'] == str(my_str):
                            self.area = y['id']
                            break

            else:
                self.area = 113     # Значение ID по умолчанию - 113(Россия)
        except GetAPIDataError:
            print(GetAPIDataError())


class SuperJobAPI(GetAPIAbstractClass):

    # Инициализация класса
    def __init__(self):
        self.__api_data = ''
        self.required_vacation = ''
        self.area = ''

    def get_api_data(self, vacation_name: str) -> None:
        """
        Получение данных с сайта SuperJob по API с запросом
        по вакансии - vacation_name, считываем максимальное
        количество страниц и собираем их в список json_data_list
        :param vacation_name:
        :return: None
        """
        if self.area.lower() in ('', 'россия'):     # Проверка, если место поиска не указано или указана страна
            user_request = {"keyword": vacation_name, "c": "1"}     # Указываем страну
        else:
            user_request = {"keyword": vacation_name, "town": self.area}    # в противном случае - город
        json_data_list = []
        api_key: str = os.getenv('SJ_API_SECRET_KEY')
        param = {'X-Api-App-Id': api_key}

        try:
            for pages in range(0, 5):       # Читаем в цикле все страницы данных по вакансиям
                request_data = {"page": pages, "count": 100}
                api_request = {**user_request, **request_data}  # Формируем запрос к api
                recs = requests.get('https://api.superjob.ru/2.0/vacancies/',
                                    headers=param,
                                    params=api_request)
                if recs.status_code != 200:
                    raise GetAPIDataError
                json_record = json.loads(recs.content.decode())    # Приводим полученные данные к формату json
                json_data_list.extend(json_record['objects'])  # Добавляем данные каждой страницы в общий список
                print(f'Загрузка страницы - {pages}')
                time.sleep(0.20)    # Задержка на запрос, чтобы не загружать сервер
        except GetAPIDataError:
            print(GetAPIDataError())
        self.__api_data = json_data_list

    def get_api_vacancy_json_list(self) -> list:
        """
        Метод для конвертации данных полученных от API SJ
        Приведение формата полученных данных к единому стандарту
        :return:
        """
        vacation_list = []
        vacancy_counter = 0
        if self.__api_data is not None:
            for data in self.__api_data:
                vacation_list.append(
                    {"id": str(data['id']),
                     "name": data['profession'],
                     "url": data['link'],
                     "salary_from": str(data['payment_from']),
                     "salary_to": str(data['payment_to']),
                     "description": data['candidat'],
                     "company": data['firm_name'],
                     "api": "SuperJob.ru"})

                vacancy_counter += 1
        else:
            print('Нет данных от SuperJob API')
        print(f'Загружено {vacancy_counter} вакансий с SuperJob.ru')
        return vacation_list