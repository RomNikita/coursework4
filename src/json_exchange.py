import json
from abc import ABC, abstractmethod

JSON_FILENAME = 'vacancy_data.json'     # Файл для сохранения вакансий


class JsonAbstract(ABC):

    @abstractmethod
    def save_raw_to_json(self, vacancies_data, vacancy_filename):
        """

        Абстрактный метод сохранения данных в файл
        :param vacancies_data: данные по вакансиям в формате json
        :param vacancy_filename: название файла
        :return:
        """
        pass

    def save_vacancy_to_json(self, vacancy_filename):
        """
        Абстрактный метод загрузки данных из файла
        :return:
        """
        pass


class JSONSaver(JsonAbstract):
    """
    Инициализация класса JSONSaver
    """
    def __init__(self):
        self.vacancies = []     # данные по вакансиям в формате json

    def save_raw_to_json(self, vacancies_data: list, vacancy_filename=JSON_FILENAME) -> None:
        """
        Запись данных от API или класса Vacancy в файл 'vacancy_data.json'
        :param vacancies_data: данные по вакансиям в формате json
        :param vacancy_filename: название файла
        :return: -> None
        """
        self.vacancies = vacancies_data
        with open(vacancy_filename, 'w', encoding='utf-8') as file:  # Открытие файла на запись
            json.dump(self.vacancies, file, ensure_ascii=False)    # Запись данных в формате json в файл
            print(f'Вакансии сохранены в файл {vacancy_filename}')   # Сообщение пользователю
        file.close()    # Закрытие файла

    def get_data_from_file(self, vacancy_filename=JSON_FILENAME) -> None:
        """
        Чтение данных из файла с вакансиями
        :param vacancy_filename: название файла
        :return:
        """
        try:
            with open(vacancy_filename, 'r', encoding='utf-8') as file:  # Открытие файла на чтение
                vacancies_data = json.load(file)    # Чтение данных из файла
                print(f'Загружено {len(list(vacancies_data))} вакансий из файла {vacancy_filename}')    # Сообщение
                self.vacancies = vacancies_data
            file.close()    # Закрытие файла
        except FileNotFoundError:
            print(f"Файл {vacancy_filename} не найден")