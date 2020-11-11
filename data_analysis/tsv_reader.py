import pandas as pd
import os
import datetime


class StockReader():
    def __init__(self):
        self.stock_data = ''
        self.tsvpath = 'D:\\PythonProject\\trading_stock\\data_collection\\dat_csv\\'
        self.code = ''
        self.extension = ''
        self.now = datetime.datetime.now()

    def get_file_name(self):
        if self.extension == 'tsv':
            return self.tsvpath + self.code + '.' + self.extension
        else:
            return self.path + self.code + '.' + self.extension

    def set_code(self, code):
        self.code = code

    def set_ext(self, extension):
        self.extension = extension

    def get_remove_comma(self):
        return self.stock_data.replace({',': ''}, regex=True)

    def sort_data(self, types="asc"):
        types = types.lower()
        if types == "asc":
            self.stock_data.sort_values(['date'], ascending=True, inplace=True)
        elif types == "desc":
            self.stock_data.sort_values(['date'], ascending=False, inplace=True)

    def stock_reader(self, s_period='', e_period=''):
        file_path = self.get_file_name()
        if os.path.exists(file_path):  # 파일 있으면
            self.stock_data = pd.read_csv(file_path, sep='\t', header=None, encoding='utf-8', names=[
                                          'date', 'close', 'diff', 'open', 'high', 'low', 'volume'])

        if e_period == '':
            e_period = str(self.now.year) + '.' + \
                str(self.now.month) + '.' + str(self.now.day)

        if s_period != '':
            self.stock_data = self.stock_data[
                (self.stock_data.date >= s_period) &
                (self.stock_data.date <= e_period)
            ]


