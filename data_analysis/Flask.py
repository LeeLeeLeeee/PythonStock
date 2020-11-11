from flask import Flask
from flask import request
import date_stock_reader as date_reader
import sys
sys.path.append('d:\\PythonProject\\trading_stock\\data_collection')
from get_main_index import MainStockIndex
from naver_sise_get import NaverSise
from get_stock_info import StockInfo



import json 

app = Flask (__name__)



@app.route('/py/read_tsv', methods = ['GET'])
def read_tsv():
    date = request.args.get("date","none")
    if date=="none":
        return date
    else:
        date = date.replace('-','')

    DSR = date_reader.DateStockReader()
    DSR.set_date(date)
    DSR.set_ext("tsv")
    DSR.stock_reader()
    return json.dumps(DSR.stock_data, ensure_ascii=False)

@app.route('/py/getIndex', methods=['GET'])
def index():
    item = request.args.get("item","KOSPI")
    msi = MainStockIndex()
    msi.set_item(item)
    return msi.crawling_info()


@app.route('/py/setNewData', methods=['GET'])
def setNewData():   
    
    code = request.args.get("code","")
    
    if code != "":
        code = code.split(",")
        naver = NaverSise()
        for x in code:
            naver.set_code(x)
            naver.file_check()
            naver.crawling_start()
        return "end"
    else:
        return "none"
    return "aa"

@app.route('/py/readStockData', methods=['GET'])
def readStockData():
    
    code = request.args.get("code","")
    current = request.args.get("current","")
    if code != "":
        code = code.split(",")
        naver_read = NaverSise()
        tsv_files = {}
        for x in code:
            naver_read.set_code(x)
            if current.lower() == "y":
                tsv_files[x] = naver_read.get_first_value()
            else:
                tsv_files[x] = naver_read.get_all_value()
                
        
        return tsv_files
    else:
        return "none"

    return "aa"

@app.route('/py/getSrim', methods=['GET'])
def readStockInfo():
    code = request.args.get("code","")
    sinfo = StockInfo()
    if code != "":
        sinfo.set_code(code)
        sinfo.get_html()
        sinfo.crawling_info()
        sinfo.get_stock_weight()
        sinfo.s_rim_calculate()
        return  {   "srim" : sinfo.s_rim,
                    "total_num" : sinfo.jusic_num,
                    "roe" : sinfo.roe,
                    "fre_ratio" : sinfo.foreiner_ratio,
                    "bsp" : sinfo.business_profits,
                    "debt_ratio" : sinfo.debt_ratio,
                    "bsp_ratio" : sinfo.business_profits_ratio
                }
    else:
        return "none"
      

        


if __name__ == "__main__":
    app.run(port=4999)
