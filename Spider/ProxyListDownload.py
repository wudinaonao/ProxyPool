import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

import requests
from Tools.Log import Log as logger
from Tools.GeneralTool import GeneralTool
import json
from Interface.ISpider import ISpider

class ProxyListDownload(ISpider):
    
    _siteurl = "https://www.proxy-list.download/api/v0/get?l=en&t="
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
    _proxyType = ""
    
    @classmethod
    def start(cls):
        logger.info("start craw proxy from https://www.proxy-list.download ...")
        
        cls._siteurl = cls._siteurl + "http"
        cls._proxyType = "HTTP"
        GeneralTool.wirteToDataBase(cls._getProxyResultList(cls._getHtml()))
        cls._siteurl = cls._siteurl + "https"
        cls._proxyType = "HTTPS"
        GeneralTool.wirteToDataBase(cls._getProxyResultList(cls._getHtml()))
        
    @classmethod
    def _getHtml(cls):
        try:
            result = requests.get(url = cls._siteurl,
                                  headers = cls._headers)
            result.encoding = "utf-8"
            return result.text
        except Exception:
            logger.error("An error occurred that get html, class ---> " + cls.__name__)

    @classmethod
    def _getProxyResultList(cls, html):
        if not html:
            logger.error("an error occurred a try craw proxy list in https://www.proxy-list.download, because html is None")
            return None
        jsonData = json.loads(html[1:-1])
        infoList = jsonData['LISTA']
        proxyDictList = []
        for info in infoList:
            try:
                if GeneralTool.isIPAddress(info['IP']) and info['ANON'].lower().strip() == "anonymous":
                    proxyDict = {}
                    proxyDict.setdefault("id", "null")
                    proxyDict.setdefault("ip", info['IP'].strip())
                    proxyDict.setdefault("port", GeneralTool.checkPortOrType("port", info['PORT'].strip()))
                    proxyDict.setdefault("type", cls._proxyType)
                    proxyDict.setdefault("location", info['COUNTRY'].strip())
                    proxyDict.setdefault("speed", "3s")
                    proxyDict.setdefault("lastUpdateTime", GeneralTool.formatDate())
                    proxyDict.setdefault("md5", GeneralTool.computeMD5(info['IP'].strip(),
                                                                       GeneralTool.checkPortOrType("port",info['PORT'].strip()),
                                                                       cls._proxyType))
                    proxyDict.setdefault("weight", "0")
                    proxyDictList.append(proxyDict)
            except Exception:
                logger.error("An error occurred while trying to get proxy dictionary in class ---> " + cls.__name__)
                logger.error(Exception)
        return proxyDictList

    
if __name__ == '__main__':
    ProxyListDownload.start()