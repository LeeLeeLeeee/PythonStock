import sys
import win32com.client as w32c
import ctypes
import pandas as pd
import os
from PyQt5.QtWidgets import *
import time
import pythoncom
import numpy as np # numpy 도 함께 import
from flask import Flask, jsonify, request


instCpCybos = w32c.Dispatch("CpUtil.CpCybos")
instCpCodeMgr = w32c.Dispatch("CpUtil.CpCodeMgr")
marketEye = w32c.Dispatch("CpSysDib.MarketEye")  # 시간대별 체결

def check_connect():
    # 프로세스가 관리자 권한으로 실행 여부
    if ctypes.windll.shell32.IsUserAnAdmin():
        print('정상: 관리자권한으로 실행된 프로세스입니다.')
    else:
        print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
        return False

    # 연결 여부 체크
    if (instCpCybos.IsConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        return False

    return True


if __name__ == "__main__":
    if not check_connect():
        print("연결에 실패하였습니다.")
        sys.exit()
    
    print(instCpCybos.GetLimitRemainCount(1))
    print("-------------------코스피-------------------")
    #print(instCpCodeMgr.GetStockListByMarket(1)) # 코스피
    print("-------------------코스닥-------------------")
    #print(instCpCodeMgr.GetStockListByMarket(2)) # 코스닥
    kosdaq = instCpCodeMgr.GetStockListByMarket(2)
    kospi = instCpCodeMgr.GetStockListByMarket(1)
    
    #kosdaq_name = [instCpCodeMgr.CodeToName(k) for k in kosdaq]
    #print(kosdaq_name)
    
    
        #주가 = EPS * PER
    field_code = [0,2,3,4,5,6,7,10,17,20,21,22,24,32,63,64,67,70,71,78,79,80,86,87,88,89,91,92,93,95,97,96,98,99,100,101,102,103,104,107,111,116,118,120,121,122,123]
    marketEye.SetInputValue(0,field_code)# 요청 값 설정
    kosdaqlength = len(kosdaq) / 200
    kospilength = len(kospi) / 200    
    item = []
    kospi_kosdaq = {
        "kospi" : {
            "list" : kospi,
            "length" : kospilength
        },
        "kosdaq" : {
            "list" : kosdaq,
            "length" : kosdaqlength
        }
    }
    kcnt = 0
    for k in kospi_kosdaq:  
        for i in range(int(kospi_kosdaq[k]["length"])):
            
            print(f'{i*199} ~ {(i+1)*199}')
            code = kospi_kosdaq[k]["list"][(i*199):(i+1)*199]
            marketEye.SetInputValue(1,code)
            marketEye.BlockRequest()
            print(str(instCpCybos.GetLimitRemainCount(1)) +  "------ 남은 횟수")

            if kcnt == 0:
                field_name = marketEye.GetHeaderValue(1)
                
            cnt = marketEye.GetHeaderValue(2)
            
            #종목 반복
            for i2 in range(cnt): 
                item.append({})
                tcnt = (kcnt * 199) + i2
                #요청값 반복
                for ii, x in enumerate(field_code):
                    item[tcnt][field_name[ii]] = marketEye.GetDataValue(ii,i2)

                item[tcnt]["업종 이름"] = instCpCodeMgr.GetIndustryName(instCpCodeMgr.GetStockIndustryCode(item[tcnt]["종목코드"]))
                try:
                    item[tcnt]["PSR"] = format(item[tcnt]["현재가"] / item[tcnt]["SPS"],".2f")
                except:
                    item[tcnt]["PSR"] = "-ERROR"
                try:
                    item[tcnt]["PBR"] = format(item[tcnt]["현재가"] / item[tcnt]["분기BPS"],".2f")
                except:
                    item[tcnt]["PBR"] = "-ERROR"
                try:
                    item[tcnt]["전일 대비 거래율"] = format( (item[tcnt]["거래량"] / item[tcnt]["전일거래량"]) * 100 - 100 ,".2f")
                except:
                    item[tcnt]["전일 대비 거래율"] = "-ERROR"
                try:
                    item[tcnt]["전일 "] = format( (item[tcnt]["거래량"] / item[tcnt]["전일거래량"]) * 100 - 100 ,".2f")
                except:
                    item[tcnt]["전일 대비 거래율"] = "-ERROR"
                    
            kcnt += 1

    print(instCpCybos.GetLimitRemainCount(1))
    df = pd.DataFrame(item)
    
    #xlsx_path = os.getcwd() + "\\trading_stock\\test\\excel_output\\" + time.strftime('%Y%m%d%H%M', time.localtime(time.time())) + ".xlsx"
    tsv_path = os.getcwd() + "\\trading_stock\\test\\stock_day_data\\" + time.strftime('%Y%m%d', time.localtime(time.time())) + ".tsv"
    #print("--코스닥 현재가 순--")
    #print(df.sort_values(by=['현재가'],ascending=False,inplace=False))
    #print("--거래량 순--")
    #print(df.sort_values(by=['거래량'],ascending=False,inplace=False))
    #print("--체결 강도 순--")
    #print(df.sort_values(by=['체결강도'],ascending=False,inplace=False))

    
    with open(tsv_path, 'w') as tsv:
        df.to_csv(sep='\t',encoding='utf-8')
        tsv.write(totaltxt)
    


"""     with pd.ExcelWriter(xlsx_path, engine='xlsxwriter') as writer:
        df.sort_values(by=['현재가'],ascending=False,inplace=False).to_excel(writer,sheet_name='현재가기준')
        writer.save() # 엑셀 저장
        os.startfile(xlsx_path) # 엑셀 실행
 """

    #df.to_json(index=False,orient="records")

 