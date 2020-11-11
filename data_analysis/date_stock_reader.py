import pandas as pd
import os
import datetime


class DateStockReader():
    def __init__(self):
        self.stock_data = []
        self.tsvpath = 'D:\\PythonProject\\trading_stock\\data_collection\\cybos_tsv\\'
        self.date = ''
        self.path = ''
        self.extension = ''
        

    def get_file_name(self):
        if self.extension == 'tsv':
            return self.tsvpath + self.date + '.' + self.extension
        else:
            return self.path + self.date + '.' + self.extension

    def set_date(self, date):
        self.date = date

    def set_ext(self, extension):
        self.extension = extension

    def get_remove_comma(self):
        return self.stock_data.replace({',': ''}, regex=True)


    def stock_reader(self):
        file_path = self.get_file_name()
        if os.path.exists(file_path):  # 파일 있으면
            with open(file_path,"r",encoding='UTF8') as tsv:
                for id, line in enumerate(tsv):
                    if line == "\n":
                        continue
                    self.stock_data.append(line.replace("\n","").split("\t"))
            
