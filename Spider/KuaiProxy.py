import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

from bs4 import BeautifulSoup as bs
import requests
from Interface.ISpider import ISpider
from Tools.Log import Log as logger
from Tools.GeneralTool import GeneralTool


class KuaiProxy(ISpider):

    
    _siteurl = "https://www.kuaidaili.com/free/inha/"
    _trakingPage = 100
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }

    @classmethod
    def start(cls):
        logger.info("start craw proxy from KuaiProxy ...")
        cls._getProxyResultLoop(cls._getHtml())
        
    @classmethod
    def _getHtml(cls):
        try:
            # concurrent handle
            # requestList = [grequests.get(cls._siteurl + str(i) + "/", timeout=10, headers=cls._headers) for i in range(1, cls._trakingPage + 1)]
            # responseList = grequests.map(requestList, size=1)
            # resultList = []
            # for response in responseList:
            #     if response is not None and response.status_code == 200:
            #         response.encoding = "utf-8"
            #         resultList.append(response.text)
            # return resultList
        
            # single handle
            resultList = []
            for i in range(1, cls._trakingPage + 1):
                response = requests.get(url=cls._siteurl + str(i) + "/", timeout=10, headers=cls._headers)
                logger.info("craw proxy from Kuai site ... {0}/{1}".format(i, cls._trakingPage))
                if response is not None and response.status_code == 200:
                    response.encoding = "utf-8"
                    resultList.append(response.text)
                else:
                    continue
            return resultList
        except Exception:
            logger.error("An error occurred that get html, class ---> " + cls.__name__)

    @classmethod
    def _getProxyResultLoop(cls, htmlList):
        for html in htmlList:
            GeneralTool.wirteToDataBase(cls._getProxyResultList(html))
    
    @classmethod
    def _getProxyResultList(cls, html):
        if not html:
            logger.error("an error occurred a try craw proxy list in KuaiProxy, because html is None")
            return None
        
        soup = bs(html, "lxml")
    
        trList = soup.find_all("tr")
        proxyDictList = []
        for tr in trList:
            rowList = []
            # for key in tr.children:
            for key in tr.descendants:
                if key.string is not None:
                    if key.string.strip():
                        rowList.append(key.string.strip())
            try:
                if GeneralTool.isIPAddress(rowList[0]):
                    proxyDict = {}
                    proxyDict.setdefault("id", "null")
                    proxyDict.setdefault("ip", rowList[0])
                    proxyDict.setdefault("port", GeneralTool.checkPortOrType("port", rowList[2]))
                    proxyDict.setdefault("type", GeneralTool.checkPortOrType("type", rowList[6]))
                    # proxyDict.setdefault("location", GeneralTool.getIpLocation(rowList[0]))
                    proxyDict.setdefault("location", rowList[8])
                    proxyDict.setdefault("speed", "3s")
                    proxyDict.setdefault("lastUpdateTime", GeneralTool.formatDate())
                    proxyDict.setdefault("md5", GeneralTool.computeMD5(rowList[0],
                                                                       GeneralTool.checkPortOrType("port", rowList[2]),
                                                                       GeneralTool.checkPortOrType("type", rowList[6])))
                    proxyDict.setdefault("weight", "0")
                    proxyDictList.append(proxyDict)
            except Exception:
                logger.error("An error occurred while trying to get proxy dictionary in class ---> " + cls.__name__)
                logger.error(Exception)
        return proxyDictList

    # @classmethod
    # def _wirteToDataBase(cls, proxyDictList):
    #     if not proxyDictList:
    #         return None
    #     try:
    #         logger.info("UnVerified table that writing proxy to the database ...")
    #         for proxyDict in proxyDictList:
    #             if not cls._database.queryIsExist("UnVerified", "md5", proxyDict['md5']):
    #                 logger.info("writing ip to unverified tabel ---> IP: {0}".format(proxyDict['ip']))
    #                 cls._database.insert("UnVerified", proxyDict)
    #     except Exception:
    #         logger.error("An error occurred in the function ---> wirteToDataBase")
    #         logger.error(Exception)
  
if __name__ == '__main__':
    
    KuaiProxy.start()