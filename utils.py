import os
import time
import random
import math


class Randomness(random.Random):
    """Constructed for making human-like delays while analyzing webpage """
    def __init__(self, seed, driver):
        super(Randomness, self).__init__(seed)
        self._driver = driver

    def wait2_rnm_seconds(self, num1, num2):
        time_awaiting = self.randint(num1,num2)
        time.sleep(time_awaiting)
        return time_awaiting

    def wait_rnm_seconds(self,num):
        time_awaiting = math.ceil(self.random()*num)
        time.sleep(time_awaiting)
        return time_awaiting


class StrTools(str):
    def _str_adjust(self, key, text):
        """
        Supposed to correct str(dict values) got by Scraper
        i.e. {'key': 'key:    data'} -> {'key': 'data'}
        """
        text = text[len(key)+1:]
        text = text.strip()
        return text


class FileManager:
    def __init__(self,path):
        self._path = path
        self._archive = []

    def _check_if_file_exists(self):
        """Checks if file with given path exists"""
        try:
            with open(self._path) as file:
                pass
        except FileNotFoundError:
            return False
        return True

    def _create_file(self):
        try:
            with open(self._path,'x') as file:
                pass
        except FileExistsError:
            print(f'File {self._path} already exists.')

    def _check_if_file_is_empty(self):
        return os.path.getsize(self._path)==0

    def archive(self,data):
        raise NotImplementedError

    def unarchive(self):
        raise NotImplementedError


class DataBase(FileManager):
    def __init__(self, db_path):
        super().__init__(db_path)
        if (not self._check_if_file_exists()):
            self._create_file()
        self.__flag = self._check_if_file_is_empty()
        self._delimeter = ';'


    def _set_columns(self,data:dict):
        try:
            with open(self._path,'a') as file:
                count = 0
                for key in data.keys():
                    count+=1
                    if count != len(data):
                        file.write(str(key)+',')
                    else:
                        file.write(str(key)+'\n')
                return True
        except Exception as e:
            print(f'{self._set_columns.__name__}; {e}')


    def _write_data_from_dict(self, file: open, dictionary):
        count = 0
        for key in dictionary.keys():
            count += 1
            if count != len(dictionary):
                file.write(str(dictionary[key]) + self._delimeter)
            else:
                file.write(str(dictionary[key]) + '\n')

    def write_to_file(self, data):
        """

        :param data: list of dicts or dict
        :return:
        """
        if self.__flag:
            try:
                if isinstance(data,list):
                    self._set_columns(data[0])
                elif isinstance(data,dict):
                    self._set_columns(data)
                else:
                    raise ValueError('given empty list or dictionary at DB class')
                self.__flag=False
            except ValueError as e:
                print(str(e) + 'at self.__flag check in DB class')

        try:
            with open(self._path,'a') as file:
                if isinstance(data, list):
                    for dictionary in data:
                        self._write_data_from_dict(file, dictionary)
                elif isinstance(data,dict):
                    self._write_data_from_dict(file,data)
                else:
                    raise TypeError('nor dict nor list were given')
        except Exception as e:
            print(f'{self.write_to_file.__name__}; {e},{e.args}')

    def archive(self,data):
        self._archive.append(data)

    def unarchive(self):
        if self._archive:
            self.write_to_file(self._archive)
            self._archive.clear()


class Logger(FileManager):
    def __init__(self, log_path):
        super().__init__(log_path)
        if (not self._check_if_file_exists()):
            self._create_file()
        self._date_offset = 17
        self._report_offset = 55

    @staticmethod
    def _get_current_time():
        return time.strftime("%Y-%m-%d  %H:%M:%S", time.localtime(time.time()))

    def _write_unarchived(self):
        with open(self._path, 'a') as file:
            for record in self._archive:
                for element in record:
                    file.write(element)

    def write_to_file(self, data):
        with open(self._path, 'a') as file:
            file.write(self._date_offset*'-'+ self._get_current_time()+ self._date_offset*'-'+'\n')
            file.write(str(data))
            file.write('\n' + self._report_offset * '-' + '\n')

    def archive(self, data):
        res = []
        res.append(self._date_offset * '-' + str(self._get_current_time()) + self._date_offset * '-' + '\n')
        res.append(str(data))
        res.append('\n' + self._report_offset * '-' + '\n')
        self._archive.append(res)

    def unarchive(self):
        self._write_unarchived()
        self._archive.clear()

