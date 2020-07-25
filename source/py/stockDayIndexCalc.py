import requests
import numpy
import pandas
import json
import sqlite3
import math
import time

from pandas import Series
from pandas import DataFrame
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException 
from requests.exceptions import ConnectionError
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class StockDayIndexCalc:
    def __init__(self):
        self.headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Accept-Encoding":"gzip, deflate, br",
                        "Host": "xueqiu.com",
                        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
                    }
        self.hostUrl = 'https://xueqiu.com'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.connectTimeout = 3
        self.respTimeout = 3
        self.session = requests.session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def prepareCalc(self, connectTimeout, respTimeout):
        self.headers["Host"] = "xueqiu.com"
        self.connectTimeout = connectTimeout
        self.respTimeout = respTimeout
     
        try:
            response = self.session.get(self.hostUrl,verify=False, headers= self.headers, timeout=(connectTimeout, respTimeout))
        except (ReadTimeout, InsecureRequestWarning, ConnectionError):
            return -1
        else:
            if (response.status_code == 200):
                return 0
            else:
                return -1


    def saveStockRealQuotes(self, data):
        try:
            itemList =  data.get('item')
            if not itemList:
                return -1
            columns = data.get('column')

            df = DataFrame(itemList, columns=columns)
            self.df = df[['open','high', 'close', 'low', 'volume']]
    
            return 0
            
        except:
            return -1


    def getStockRealQuotes(self, stockNo, counts):
        orgUrl = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={stockNo}&begin={beginTime}&period=day&type=before&count={counts}&indicator=kline'
        url = orgUrl.format(stockNo=stockNo, beginTime = int(time.time())*1000, counts=counts*(-1))
    
        self.headers["Host"] = "stock.xueqiu.com"
        try:
            response = self.session.get(url, verify=False, headers = self.headers, timeout=(self.connectTimeout, self.respTimeout))
        except (RequestException, ConnectionError, TooManyRedirects):
            return -1
        else:
            if (response.status_code == 200):
                resData = response.json().get('data', None)
                if not resData:
                    return -1

                ret = self.saveStockRealQuotes(resData)
                return ret
            else:
                return -1


    def calcStockMa(self, windowSize):
        ma = self.df['close'].rolling(window=windowSize, min_periods=1).mean()
        return ma

    def calcStockCCI(self, windowN, windowM):
        cciType = (self.df['close']+self.df['high']+self.df['low'])/3
        cciTypeMa = cciType.rolling(window=windowN, min_periods=1).mean()
        cciTypeDev = (cciType-cciTypeMa)
        cciTypeAvedev = cciTypeDev.abs().rolling(window=windowN, min_periods=1).mean()
        print(cciType)
        print('--------')
        print(cciTypeAvedev)
        cci = cciTypeDev/(0.015*cciTypeAvedev)
        print('--------')
        print(cci)


        
if __name__ == '__main__':
    stockDayCacl =   StockDayIndexCalc()
    if (not stockDayCacl.prepareCalc(3, 3)):
        """
        ret = weekKLine.getAndUpdateStockList(int(time.time()))
        
        ret = weekKLine.getAndUpdateWeekKLine('SZ300599', int(time.time()), -1)
       
        ret = weekKLine.getCurWeekKLine('SZ300001')
        """
        ret = stockDayCacl.getStockRealQuotes('SH603488', 50)
        if not ret:
            stockDayCacl.calcStockCCI(14,5)
     


        
