from technical_analysis import TechnicalAnalysis
from tsv_reader import StockReader

sr = StockReader()
tas = TechnicalAnalysis()

sr.set_code('161580')
sr.set_ext('tsv')
sr.stock_reader('2020.01.01')
sr.sort_data("asc")

tas.set_code(sr.code)
tas.set_stock_data(sr.get_remove_comma())
tas.cal_sma()
print(tas.analysis_data)

