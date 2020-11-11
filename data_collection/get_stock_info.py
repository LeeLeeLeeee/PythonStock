import requests
import json
from bs4 import BeautifulSoup
import os
import math
import sys


class StockInfo():
    def __init__(self):
        self.code = ''
        self.weight = ''
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'charset': 'utf-8'
        }
        self.jusic_num = ''
        self.my_stock_number = ''
        self.roe = ''
        self.foreiner_ratio = ''
        self.business_profits = ''
        self.debt_ratio = ''
        self.business_profits_ratio = ''
        self.distribution_stock_number = ''
        self.my_capital = ''
        self.s_rim = []
    def set_code(self, code):
        self.code = code

    def get_stock_weight(self): # 회사채 구하기
        url = f'https://www.kisrating.com/ratingsStatistics/statics_spread.do'
        res = requests.get(url, headers=self.header)
        bs = BeautifulSoup(res.content, 'lxml')
        self.weight = bs.select("#con_tab1 > div.table_ty1 > table > tbody > tr:nth-child(11) > td:nth-child(9)")[0].get_text()
        self.weight = float(self.weight) / 100
    def get_html(self):
        url = f'http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A' + self.code
        res = requests.get(url, headers=self.header)
        return res.content

    def crawling_info(self):
        html_text = self.get_html()
        bs = BeautifulSoup(html_text, 'lxml')
        jaemu = bs.select("#highlight_D_A > table > tbody > tr")
        sise = bs.select("#svdMainGrid1 > table > tbody > tr")
        my_stock_number = bs.select("#svdMainGrid5 > table > tbody > tr:nth-child(5) > td:nth-child(3)")
        
        self.my_capital = list(map(lambda e: e.get_text().replace(",","").replace(u'\xa0',""), jaemu[9].select('td')[:4])) # 자기자본
        self.my_capital =  list(map(lambda cost: 0 if cost.strip() == '' else int(cost) * 100000000, self.my_capital))
        self.jusic_num  = sise[6].select('td')[0].get_text() # 총 주식 수
        self.jusic_num = int(self.jusic_num.split("/")[0].replace(",","").replace (u'\xa0',"")) # 총 주식 수
        self.my_stock_number = int(my_stock_number[0].get_text().replace(",","").replace (u'\xa0',"")) # 자사주
        self.distribution_stock_number  = self.jusic_num - self.my_stock_number # 유통 주식수
        self.roe = list(map(lambda e: e.get_text().replace (u'\xa0',""), jaemu[17].select('td')[:5])) # roe
        self.roe = list(map(lambda roe: 0 if roe =='' else roe, self.roe)) # roe
        self.foreiner_ratio = sise[3].select('td')[1].get_text().replace (u'\xa0',"") # 외국인 비율
        self.business_profits = list(map(lambda e: e.get_text().replace (u'\xa0',""), jaemu[1].select('td')[:4])) # 영업이익
        self.business_profits = list(map(lambda item: 0 if item == '' else item, self.business_profits)) # 0 처리
        self.debt_ratio = list(map(lambda e: e.get_text().replace (u'\xa0',""), jaemu[12].select('td')[:4])) # 부채비율        
        self.debt_ratio = list(map(lambda item: 0 if item == '' else item, self.debt_ratio)) # 0 처리
        self.business_profits_ratio = list(map(lambda e: e.get_text().replace (u'\xa0',""), jaemu[14].select('td')[:4])) # 영업이익률
        self.business_profits_ratio = list(map(lambda item: 0 if item == '' else item, self.business_profits_ratio)) # 0 처리

        
    def s_rim_calculate(self):
        roe_average = 0
        for i, roe in enumerate(self.roe[:3]):
            roe_average = roe_average + (float(roe) * (int(i)+1) )

        roe_average = round(roe_average / 6, 2) / 100 # 3년 가중평균 roe
        exceed_profit = self.my_capital[2] * (roe_average - self.weight) # 초과이익
        company_value = self.my_capital[2] + (exceed_profit / self.weight) # 기업가치
        # roe 감소시 기업 가치
        minus_company_value = list(map(lambda r: self.my_capital[2] + (exceed_profit * (r/( 1 + self.weight - r))) ,[0.9, 0.8, 0.7, 0.6, 0.5]))
        self.s_rim.append(int(company_value / self.distribution_stock_number))
        for cp_value in minus_company_value:
            self.s_rim.append(int(cp_value / self.distribution_stock_number))
        
        