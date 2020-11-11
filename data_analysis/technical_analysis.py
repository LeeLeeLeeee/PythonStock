import talib.abstract as ta


class TechnicalAnalysis():

    def __init__(self):
        self.code = ""
        self.high = ""
        self.low = ""
        self.close = ""
        self.date = ""
        self.volume = ""
        self.open = ""
        self.analysis_data = {}

    def set_code(self, code):
        self.code = code

    def set_stock_data(self, stock_data):
        self.high = stock_data['high']
        self.low = stock_data['low']
        self.close = stock_data['close']
        self.volume = stock_data['volume']
        self.date = stock_data['date']
        self.open = stock_data['open']

    #CCI
    def cal_cci(self, period=14):
        self.analysis_data['cci'] = ta.CCI(
            self.high, self.low, self.close, timeperiod=period)

    def cal_rsi(self, period=60):
        self.analysis_data['rsi'] = ta.RSI(self.close, timeperiod=period)

    def cal_macd(self, fast=12, slow=26, signal=9):
        macd, macdsignal, macdhist = ta.MACD(
            self.close, fastperiod=fast, slowperiod=slow, signalperiod=signal)

        self.analysis_data['macd'] = macd
        self.analysis_data['macdsignal'] = macdsignal
        self.analysis_data['macdhist'] = macdhist

    def cal_obv(self):
        self.analysis_data['obv'] = ta.OBV(self.close, self.volume)

    def cal_bb(self, period=20):
        upperband, middleband, lowerband = ta.BBANDS(self.close, timeperiod=period, nbdevup=2.0, nbdevdn=2.0, matype=0)

        self.analysis_data['upperband']     = upperband
        self.analysis_data['middleband']    = middleband
        self.analysis_data['lowerband']     = lowerband

    def cal_sma(self):
        self.analysis_data['sma5']      = ta.SMA(self.close, timeperiod=5)
        self.analysis_data['sma20']     = ta.SMA(self.close, timeperiod=20)
        self.analysis_data['sma60']     = ta.SMA(self.close, timeperiod=60)
        self.analysis_data['sma120']    = ta.SMA(self.close, timeperiod=120)

    def cal_wma(self):
        self.analysis_data['wma5']      = ta.WMA(self.close, timeperiod=5)
        self.analysis_data['wma20']     = ta.WMA(self.close, timeperiod=20)
        self.analysis_data['wma60']     = ta.WMA(self.close, timeperiod=60)
        self.analysis_data['wma120']    = ta.WMA(self.close, timeperiod=120)
