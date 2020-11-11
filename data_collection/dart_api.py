import requests
import zipfile
import io
import json
import os
import sys
import pandas as pd
from lxml import etree


class DartApi():
    def __init__(self):
        self.APKEY = '551e727271be981152553a376129562eaeac707b'
        self.path = os.getcwd()+'\\'+'trading_stock\\store\\CORPCODE.xml'

    def set_code(self, code):
        self.code = code

    def get_dartcode_xml(self):
        return etree.parse(self.path).getroot()

    def change_dartcode_to_stock(self):
        root = self.get_dartcode_xml()
        for list_code in root.iter('list'):
            if list_code.find('stock_code').text == ' ':
                root.remove(list_code)
            else:
                list_code.set('scode', list_code.find('stock_code').text)

        tree.write(self.path, encoding='utf8', xml_declaration=True)

    def get_dartcode_by_stock(self, stock):
        root = self.get_dartcode_xml()
        fe = root.find(f'list[@scode="{stock}"]')
        self.code = fe.find('corp_code').text
        return self.code

    def get_single_info(self, bsn_year='2020', rcode='11013'):
        # rcode => 11013[1분기 보고서], 11012[반기 보고서], 11014[3분기 보고서], 11011[사업 보고서]
        url = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'
        param = {
            'crtfc_key' : self.APKEY,
            'corp_code' : self.code,
            'bsns_year' : bsn_year,
            'reprt_code': rcode
        }
        res = requests.get(url,params=param)
        if res.status_code == 200:
            print(res.text)


da = DartApi()
da.get_dartcode_by_stock('161580')
da.get_single_info()
