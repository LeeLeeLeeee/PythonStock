import sys
import win32com.client as w32c
import ctypes
import pandas as pd
import os
from PyQt5.QtWidgets import *
import time
import pythoncom


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

    

    code = ["A083310","A003490"]
    #주가 = EPS * PER
    field_code = [0,4,6,7,10,17,22,67,70,96,123,107]
    marketEye.SetInputValue(0,field_code)# 요청 값 설정 [-종목코드,현재가,고가,저가,거래량,체결강도,PER(주가 수익 비율),EPS(주당 순이익),SPS(주당 매출액),분기ROE] 
    marketEye.SetInputValue(1,code)
    marketEye.BlockRequest()
    fcnt = marketEye.GetHeaderValue(0)
    field_name = marketEye.GetHeaderValue(1)
    
    cnt = marketEye.GetHeaderValue(2)
    item = []
    #종목 반복
    for i in range(cnt): 
        item.append({})
        #요청값 반복
        for ii, x in enumerate(field_code):
            item[i][field_name[ii]] = marketEye.GetDataValue(ii,i)

        item[i]["PSR"] = format(item[i]["현재가"] / item[i]["SPS"],".2f")
        print(item[i])
    
