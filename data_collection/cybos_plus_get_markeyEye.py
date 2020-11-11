import sys
import win32com.client as w32c
import ctypes
import pandas as pd
import os
import time
import numpy as np  # numpy 도 함께 import
import pythoncom

class GetMarketSise():

    def __init__(self):
        # 모듈
        self.instCpCodeMgr = w32c.Dispatch("CpUtil.CpCodeMgr")
        self.marketEye = w32c.Dispatch("CpSysDib.MarketEye")  # 시간대별 체결
        self.instCpCybos = w32c.Dispatch("CpUtil.CpCybos")
        
        # 요청 값 설정
        self.field_code = [0, 2, 3, 4, 5, 6, 7, 10, 17, 20, 21, 22, 23, 24, 32, 63, 64, 67, 70, 71, 75, 77, 78, 79, 80, 86, 87,
                           88, 89, 91, 92, 93, 95, 97, 96, 98, 99, 100, 101, 102, 103, 104, 107, 111, 116, 118, 120, 121, 122, 123]

        # 출력용 ITEM
        self.item = []

        # 코스피 코스닥 묶음. 반복문 용
        self.kospi_kosdaq = {
            "kospi": {
                "list": "",
                "length": ""
            },
            "kosdaq": {
                "list": "",
                "length": ""
            }
        }

        # 전체 카운트
        self.kcnt = 0

        # 필드 명
        self.field_name = ""

        # 데이터 프레임
        self.df = ""

        # tsv 파일 경로
        self.tsv_path = ""
        # xlsx 파일 경로
        self.xlsx_path = ""


    def set_path(self, date):
        base_path = os.getcwd()
        self.tsv_path = base_path + "\\trading_stock\\data_collection\\cybos_tsv\\" + date + ".tsv"
        self.xlsx_path = base_path + "\\trading_stock\\data_collection\\cybos_xlsx\\" + date + ".xlsx"

    def check_remain_count(self):  # 남아있는 검색 개수 60번 => 15초 기다림.
        return str(self.instCpCybos.GetLimitRemainCount(1))

    def get_kospi_list(self):  # 코스피 리스트 체크
        return self.instCpCodeMgr.GetStockListByMarket(1)

    def get_kosdaq_list(self):  # 코스닥 리스트 체크
        return self.instCpCodeMgr.GetStockListByMarket(2)

    def set_market_header(self):
        self.marketEye.SetInputValue(0, self.field_code)

    def select_market_list(self, lists):
        self.marketEye.SetInputValue(1, lists)

    def set_list_range(self, target, i):
        return target["list"][(i*199):(i+1)*199]

    def get_request_list(self):
        return self.marketEye.GetHeaderValue(2)

    def get_request_field_name(self):
        return self.marketEye.GetHeaderValue(1)

    def make_data_frame(self):
        self.df = pd.DataFrame(self.item)

    def write_file_tsv(self):
        with open(self.tsv_path, 'w', encoding='utf8') as tsv:
            tsv_txt = self.df.to_csv(sep='\t', encoding='utf-8')
            tsv.write(tsv_txt)

    def write_file_xlsx(self):
        with pd.ExcelWriter(self.xlsx_path, engine='xlsxwriter') as writer:
            #df.sort_values(by=['현재가'],ascending=False,inplace=False) 정렬

            self.df.to_excel(writer,sheet_name='')
            writer.save() # 엑셀 저장
            os.startfile(self.xlsx_path) # 엑셀 실행

    def get_business_name(self, code):
        return self.instCpCodeMgr.GetIndustryName(self.instCpCodeMgr.GetStockIndustryCode(code))


    def search_start(self):
        # 파일 경로 설정
        
        self.set_path( time.strftime('%Y%m%d', time.localtime(time.time())) )

        #코스피 리스트 및 길이
        kospi = self.get_kospi_list()
        
        self.kospi_kosdaq["kospi"]["list"] = kospi
        self.kospi_kosdaq["kospi"]["length"] = len(kospi) / 200 # 최대 요청 길이 제한 200

        #코스닥 리스트 및 길이
        kosdaq = self.get_kosdaq_list()
        self.kospi_kosdaq["kosdaq"]["list"] = kosdaq
        self.kospi_kosdaq["kosdaq"]["length"] = len(kosdaq) / 200 # 최대 요청 길이 제한 200

        # 요청 값 설정
        self.set_market_header()
        for k in self.kospi_kosdaq:
            for i in range(int(self.kospi_kosdaq[k]["length"])):
                code = self.set_list_range(self.kospi_kosdaq[k], i)
                self.select_market_list(code)
                self.marketEye.BlockRequest()
                print("Remain count----" + self.check_remain_count() + "----")
                if self.kcnt == 0:
                    self.field_name = self.get_request_field_name()

                # 전달 받은 리스트 개수
                cnt = self.get_request_list()

                for i2 in range(cnt): 
                    self.item.append({})
                    tcnt = (self.kcnt * 199) + i2
                    #요청값 반복
                    for ii, x in enumerate(self.field_code):
                        self.item[tcnt][self.field_name[ii]] = self.marketEye.GetDataValue(ii,i2)
    
                    self.item[tcnt]["업종 이름"] = self.get_business_name(self.item[tcnt]["종목코드"])

                    try:
                        self.item[tcnt]["PSR"] = format(self.item[tcnt]["현재가"] / self.item[tcnt]["SPS"],".2f")
                    except:
                        self.item[tcnt]["PSR"] = "-ERROR"
                    try:
                        self.item[tcnt]["PBR"] = format(self.item[tcnt]["현재가"] / self.item[tcnt]["분기BPS"],".2f")
                    except:
                        self.item[tcnt]["PBR"] = "-ERROR"
                    try:
                        self.item[tcnt]["전일 대비 거래율"] = format( (self.item[tcnt]["거래량"] / self.item[tcnt]["전일거래량"]) * 100 - 100 ,".2f")
                    except:
                        self.item[tcnt]["전일 대비 거래율"] = "-ERROR"
                    try:
                        self.item[tcnt]["등락/수익(비율)"] = format( (self.item[tcnt]["현재가"] / self.item[tcnt]["전일종가"]) * 100 - 100 ,".2f")
                    except:
                        self.item[tcnt]["등락/수익(비율)"] = "-ERROR"
                    
                self.kcnt += 1
                