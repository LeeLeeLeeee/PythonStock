import sys
import win32com.client as w32c
import ctypes
import pandas as pd
import os
from PyQt5.QtWidgets import *
import time
import win32event
import pythoncom


instCpCybos = w32c.Dispatch("CpUtil.CpCybos")
instCpCodeMgr = w32c.Dispatch("CpUtil.CpCodeMgr")
stockBid = w32c.Dispatch("Dscbo1.StockBid")  # 시간대별 체결
StopEvent = win32event.CreateEvent(None, 0, 0, None)

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



def MessagePump(timeout):
    waitables = [StopEvent]
    while 1:
        rc = win32event.MsgWaitForMultipleObjects(
            waitables,
            0,  # Wait for all = false, so it waits for anyone
            timeout, #(or win32event.INFINITE)
            win32event.QS_ALLEVENTS)  # Accepts all input
 
        if rc == win32event.WAIT_OBJECT_0:
            # Our first event listed, the StopEvent, was triggered, so we must exit
            print('stop event')
            break
 
        elif rc == win32event.WAIT_OBJECT_0 + len(waitables):
            # A windows message is waiting - take care of it. (Don't ask me
            # why a WAIT_OBJECT_MSG isn't defined < WAIT_OBJECT_0...!).
            # This message-serving MUST be done for COM, DDE, and other
            # Windowsy things to work properly!
            print('pump')
            if pythoncom.PumpWaitingMessages():
                break  # we received a wm_quit message
        elif rc == win32event.WAIT_TIMEOUT:
            print('timeout')
            return
            pass
        else:
            print('exception')
            raise RuntimeError("unexpected win32wait return value")


class CpEvent():
    def set_params(self, client, name, caller):
        self.client = client
        self.name = name
        self.caller = caller

    def OnReceived(self):
        cnt = self.client.GetHeaderValue(2)
        
        if self.name == "stockBid":  # 시간대별 체결
            for i in range(cnt):
                item = {}  # Dict
                item['시간'] = self.client.GetDataValue(0, i)
                item['시가'] = self.client.GetDataValue(1, i)
                item['고가'] = self.client.GetDataValue(2, i)
                item['저가'] = self.client.GetDataValue(3, i)
                item['종가'] = self.client.GetDataValue(4, i)
                #print(item)
        print('recieved')
        win32event.SetEvent(StopEvent)
        return

class CpStock:
    def __init__(self, objEvent):
        self.name = "stockBid"
        self.obj = objEvent
 
    def Subscribe(self):
        handler = w32c.WithEvents(self.obj, CpEvent)
        handler.set_params(self.obj, self.name, None)
 

if __name__ == "__main__":
    if not check_connect():
        print("연결에 실패하였습니다.")
        sys.exit()

    code = "A083310"

    for x in range(15):
        print(instCpCodeMgr.CodeToName(code))
        print(instCpCybos.GetLimitRemainCount(1))
        stockBid.SetInputValue(0, code)
        stockBid.SetInputValue(2, ord("1"))
        stockBid.SetInputValue(4, str(1030 + x ))
        objReply = CpStock(stockBid)
        objReply.Subscribe()
        stockBid.Request()
        MessagePump(100)
        print(instCpCybos.GetLimitRemainCount(1))
        time.sleep(1)

    
