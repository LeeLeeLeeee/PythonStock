import sys
import win32com.client as w32c
import ctypes
import os

class CheckAbleCybos():
    def __init__(self):
        self.instCpCybos = w32c.Dispatch("CpUtil.CpCybos")
        print("클래스 생성")

    def __call__(self):
        print("인스턴스 생성")

    def check_connect(self):
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                print('정상: 관리자권한으로 실행된 프로세스입니다.')
            else:
                print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
                return False

            if (self.instCpCybos.IsConnect == 0):
                print("PLUS가 정상적으로 연결되지 않음. ")
                return False

            return True
        except:
            print("에러 발생")
