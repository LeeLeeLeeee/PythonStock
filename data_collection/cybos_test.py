from cybos_plus_get_markeyEye import GetMarketSise
from check_connection import CheckAbleCybos

check = CheckAbleCybos()

if not check.check_connect():
    print("ERROR 발생")
else:
    today_markey_sise = GetMarketSise()
    today_markey_sise.search_start()
    today_markey_sise.make_data_frame()
    today_markey_sise.write_file_xlsx()
    today_markey_sise.write_file_tsv()
    