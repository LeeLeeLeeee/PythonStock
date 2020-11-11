import requests
import json
from bs4 import BeautifulSoup
import os
import math
import sys


class MainStockIndex():
    def __init__(self):
        self.item = ''
        self.header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
            'charset': 'utf-8'
        }

    def set_item(self, item):
        self.item = item

    def get_index_html(self):
        url = f'https://finance.naver.com/sise/sise_index.nhn?code=' + self.item
        res = requests.get(url, headers=self.header)
        return res.content

    def crawling_info(self):
        info = {
            "now_value": {
                "up_dn": "",
                "value": "",
                "fluc_v": "",
                "fluc_ratio": ""
            },
            "trade_trend": {
                "indi": {
                    "value": "",
                    "up_dn": ""
                },
                "com": {
                    "value": "",
                    "up_dn": ""
                },
                "foreigner": {
                    "value": "",
                    "up_dn": ""
                },
            },
            "stock_summary": []

        }
        html_text = self.get_index_html()
        bs = BeautifulSoup(html_text, 'lxml')
        detail = bs.select_one("#quotient")
        lst_info = bs.select(".lst_kos_info dd > span")
        stock_summary = bs.select(".table_kos_index .td3 > ul > li > a")

        for i, item in enumerate(lst_info[:3]):
            this_target = ""
            if i == 0:
                this_target = info["trade_trend"]["indi"]
            elif i == 1:
                this_target = info["trade_trend"]["foreigner"]
            elif i == 2:
                this_target = info["trade_trend"]["com"]

            this_target["up_dn"] = item['class'][0]
            this_target["value"] = item.text

        info["stock_summary"] = list(map(lambda x: x.text, stock_summary))
        if len(detail['class']) == 2:
            info["now_value"]["up_dn"] = detail['class'][1]
            info["now_value"]["value"] = detail.select("em")[0].get_text()
            fluc = detail.select("#change_value_and_rate")[0].get_text().split(" ")
            info["now_value"]["fluc_v"] = fluc[0]
            info["now_value"]["fluc_ratio"] = fluc[1]

        return info
