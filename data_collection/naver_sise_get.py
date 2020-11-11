import requests
import json
from bs4 import BeautifulSoup
import os
import datetime
import csv
import math
import sys


class NaverSise():
    def __init__(self):
        self.code = ''
        self.code_first_date = ''
        self.min = 1
        self.max = 100
        self.now = datetime.datetime.now()
        self.nowDate = datetime.datetime.date(self.now)
        self.path = 'D:\\PythonProject\\trading_stock\\data_collection\\dat_csv\\'
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
        self.list_tsv = ''
        self.skip = False
    def set_code(self, code):
        self.code = code

    def get_file_name(self):
        return self.path + self.code + '.tsv'

    # 날짜 차이 계산 (self, 비교할 날짜) => 순수 날짜 차이, 차이 / 5
    def get_date_diff(self):
        f_date_diff = self.nowDate - self.code_first_date
        n_diff = f_date_diff.days  # 일 차이 계산
        pp = math.floor(n_diff / 5)  # 5로 나눔 => 페이지 검색 최소화 위해..
        return n_diff, pp

    # 첫번째 Row만 읽어옴
    def get_first_value(self):
        with open(self.get_file_name()) as f:
            first_line = f.readline()
        return first_line.split("\t")

    # 전체 파일 읽어옴
    def get_all_value(self):
        file_path = self.get_file_name()
        if os.path.exists(file_path):  # 파일 있으면
            with open(file_path, 'r', encoding='utf-8') as f:
                file_tsv = csv.reader(f, delimiter='\t')
                return list(file_tsv)
        else:
            return False
            
    # 파일 유무 체크, 파일 있을 경우 첫 번째 날자 가져옴
    def file_check(self):
        
        self.code_first_date = ''
        self.list_tsv = ''

        file_path = self.get_file_name()
        file_tsv = ''

        if os.path.exists(file_path):  # 파일 있으면
            with open(file_path, 'r', encoding='utf-8') as f:
                file_tsv = csv.reader(f, delimiter='\t')
                self.list_tsv = list(file_tsv)[1:]  # 파일을 리스트로 변경 => 가장 최근 날짜는 리스트 서 제외함.
                if len(self.list_tsv) > 0:  # 파일에 내용이 있는 지
                    self.code_first_date = self.list_tsv[0][0]
                    if self.code_first_date == "":
                        self.skip = True
                    t_date = self.code_first_date.split('.')  # 파일 상 날짜만 연,월,일로 구분
                    self.code_first_date = datetime.date(
                                                int(t_date[0]), int(t_date[1]), int(t_date[2]))
    # 크롤링 타입 체크 (신규, 수정)
    def crawling_start(self):
        if self.code_first_date == '':
            self.max = 100
            self.file_write_type = 'new'
            self.crawling_data_new()
        else:
            diff_days, pp = self.get_date_diff()
            self.file_write_type = 'update'
            self.crawling_data_update(pp)

    # 네이버 시세 html 통신
    def get_sise_html(self, page):
        url = f'https://finance.naver.com/item/sise_day.nhn?code={self.code}&page={page}'
        res = requests.get(url, headers=self.header)
        return res.text

    # 신규용 수집
    def crawling_data_new(self):
        total_text = '' # 파일에 저장할 전체값
        html_text = '' # 받아온 html
        prev_text = '' # 이전 페이지 html // 비교용

        for i in range(self.min, self.max):
            html_text = self.get_sise_html(i)
            if prev_text == html_text:
                break

            bs = BeautifulSoup(html_text, 'lxml')
            for id, tr in enumerate(bs.find('table').findAll('tr')):
                td = tr.findAll('td')
                if len(td) != 7:
                    continue
                else:
                    row_text = [td.get_text().strip()
                                for tid, td in enumerate(td)]
                    img = tr.find("img")
                    if img != None:
                        if img["src"].find("down") > 0:
                            row_text[2] = "-" + row_text[2]

                    txt = '\t'.join(row_text)
                    total_text += txt + '\n'
            prev_text = html_text

        self.write_file(total_text)

    # 수정용 수집
    def crawling_data_update(self, pp):
        add_list = []
        today_flag = False
        for i in range(1, (2+pp)):  # 날짜 차이가 나는 만큼 반복문 증가
            html_text = self.get_sise_html(i)
            bs = BeautifulSoup(html_text, 'lxml')
            for id, tr in enumerate(bs.find('table').findAll('tr')):
                td = tr.findAll('td')

                if len(td) == 7:
                    row_data = [td.get_text().strip()
                                for tid, td in enumerate(td)]
                    if row_data[0] == "":
                        break

                    row_date = row_data[0].split(".")  # 페이지 상의 날짜 검색
                    f_row_date = datetime.date(
                        int(row_date[0]), int(row_date[1]), int(row_date[2]))
                    r_diff = (f_row_date - self.code_first_date)
                    
                    if r_diff.days > -1:  # 저장된 데이터중 가장 최근 데이터와 페이지 상의 날짜에 차이가 있다면 list에 저장
                        img = tr.find("img")
                        if img != None:
                            if img["src"].find("down") > 0:
                                row_data[2] = "-" + row_data[2]

                        add_list.append(row_data)

                        if r_diff.days == 0:
                            today_flag = True
                            break;   

        if today_flag:
            self.list_tsv = add_list + self.list_tsv[1:]
        else:
            self.list_tsv = add_list + self.list_tsv

        self.write_file(False)

    def write_file(self, totaltxt):
        file_path = self.get_file_name()
        with open(file_path, 'w') as tsv:
            if self.file_write_type == 'new':
                tsv.write(totaltxt)
            else:
                for r in self.list_tsv:
                    tsv.writelines('\t'.join(r) + '\n')
