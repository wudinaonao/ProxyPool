import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])


from bs4 import BeautifulSoup as bs
import requests
from Interface.ISpider import ISpider
from Tools.Log import Log as logger
from Tools.GeneralTool import GeneralTool



class CnProxy(ISpider):

    _siteurl = "https://cn-proxy.com/"

    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }

    
    @classmethod
    def start(cls):
        logger.info("start craw proxy from CnProxy ...")
        GeneralTool.wirteToDataBase(cls._getProxyResultList(cls._getHtml()))

    @classmethod
    def _getHtml(cls):
    
        try:
            result = requests.get(url=cls._siteurl,
                                  headers=cls._headers)
            result.encoding = "utf-8"
            return result.text
        except Exception:
            logger.error("An error occurred that get html, class ---> " + cls.__name__)

    @classmethod
    def _getProxyResultList(cls, html):
        if not html:
            logger.error("an error occurred a try craw proxy list in CnProxy, because html is None")
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
                    proxyDict.setdefault("type", "HTTP")
                    # proxyDict.setdefault("location", GeneralTool.getIpLocation(rowList[0]))
                    proxyDict.setdefault("location", rowList[4])
                    proxyDict.setdefault("speed", "3s")
                    proxyDict.setdefault("lastUpdateTime", GeneralTool.formatDate())
                    proxyDict.setdefault("md5", GeneralTool.computeMD5(rowList[0],
                                                                       GeneralTool.checkPortOrType("port", rowList[2]),
                                                                       "HTTP"))
                    proxyDict.setdefault("weight", "0")
                    proxyDictList.append(proxyDict)
            except Exception:
                logger.error("An error occurred while trying to get proxy dictionary in class ---> " + cls.__name__)
                logger.error(Exception)
        return proxyDictList
        
if __name__ == '__main__':
    
    CnProxy.start()