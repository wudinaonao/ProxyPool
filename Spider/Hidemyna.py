import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

import grequests
from bs4 import BeautifulSoup as bs
import requests
import time
from Tools.Log import Log as logger
from Tools.GeneralTool import GeneralTool
import execjs
from Interface.ISpider import ISpider


class Hidemyna(ISpider):
    
    _siteurl = "https://hidemyna.me/en/proxy-list/?type=hs&anon=4&start="
    _trakingPage = 10
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
    
    @classmethod
    def start(cls):
        logger.info("start craw proxy from Hidemyna Proxy ...")
        cls._getProxyResultLoop(cls._getHtml())
        
    @classmethod
    def _getProxyResultLoop(cls, htmlList):
        for html in htmlList:
            GeneralTool.wirteToDataBase(cls._getProxyResultList(html))
            
    @classmethod
    def _getHtml(cls):
        try:
            # concurrent handle
            cookies = cls._getCookies()
            if not "cf_clearance" in cookies.keys():
                logger.error("get site https://hidemyna.me/en/proxy-list/ cookies failed")
                return []
            requestList = [grequests.get(url=cls._siteurl + str(i * 64), timeout=10, headers=cls._headers, cookies=cookies) for i in range(0, cls._trakingPage + 1)]
            responseList = grequests.map(requestList, size=10)
            resultList = []
            for response in responseList:
                if response is not None and response.status_code == 200:
                    response.encoding = "utf-8"
                    resultList.append(response.text)
            return resultList
            # single handle
            # resultList = []
            # cookies = cls._getCookies()
            # if not "cf_clearance" in cookies.keys():
            #     logger.error("get site https://hidemyna.me/en/proxy-list/ cookies failed")
            #     return resultList
            # for i in range(cls._trakingPage):
            #     response = requests.get(url=cls._siteurl + str(i * 64), timeout=10, headers=cls._headers, cookies=cookies)
            #     logger.info("craw proxy from Hidemyna site ... {0}/{1}".format(i, cls._trakingPage))
            #     if response is not None and response.status_code == 200:
            #         response.encoding = "utf-8"
            #         resultList.append(response.text)
            #     else:
            #         continue
            # return resultList
        except Exception:
            logger.error("An error occurred that get html, class ---> " + cls.__name__)
    
    @classmethod
    def _getProxyResultList(cls, html):
        if not html:
            logger.error("an error occurred a try craw proxy list in Hidemyna Proxy, because html is None")
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
                    proxyDict.setdefault("port", GeneralTool.checkPortOrType("port", rowList[3]))
                    proxyDict.setdefault("type", GeneralTool.checkPortOrType("type", rowList[7]))
                    # proxyDict.setdefault("location", GeneralTool.getIpLocation(rowList[0]))
                    proxyDict.setdefault("location", rowList[4])
                    proxyDict.setdefault("speed", "3s")
                    proxyDict.setdefault("lastUpdateTime", GeneralTool.formatDate())
                    proxyDict.setdefault("md5", GeneralTool.computeMD5(rowList[0],
                                                                       GeneralTool.checkPortOrType("port", rowList[3]),
                                                                       GeneralTool.checkPortOrType("type", rowList[7])))
                    proxyDict.setdefault("weight", "0")
                    proxyDictList.append(proxyDict)
            except Exception:
                logger.error("An error occurred while trying to get proxy dictionary in class ---> " + cls.__name__)
                logger.error(Exception)
        return proxyDictList
    
    @classmethod
    def _getAnswer(cls, html):
        '''
        input 503 html for get jschl_answer value
        :param html:
        :return:
        '''
        # get script
        script = html[html.find('<script type="text/javascript">'): html.find('</script>')]
        rowList = script.split("\n")
        secretName = ""
        secretKey = ""
        secret1 = ""
        secret2 = ""
        # split row use to \n
        for row in rowList:
            if "var s,t,o,p,b,r,e,a,k,i,n,g,f, " in row:
                secret1 = row.split(" ")[-1].strip()[: -1]
                secretName = secret1.split("=")[0].strip()
                secretKey = secret1.split('"')[1].strip()
            if secretName:
                if secretName in row:
                    secret2Raw = row.split(";")
                    for element in secret2Raw:
                        if element.startswith(secretName):
                            secret2 += element + ";"
        # ready run js
        if secret1 and secret2 and secretName and secretKey:
            # merge javascript
            js = "function secret() {" + \
                 secret1 + ";" + \
                 secret2 + ";" + \
                 "return (+" + secretName + "." + secretKey + " + 11).toFixed(10);}"
            jsFunction = execjs.compile(js)
            secret = jsFunction.call('secret')
            return secret
        return ""
    
    @classmethod
    def _getRequestParams(cls, html):
        '''
        get request params use to get cookies
        :param html:
        :return:
        '''
        s = ""
        jschlVc = ""
        passValue = ""
        for row in html.split('\n'):
            if 'name="s"' in row:
                s = row.split('value="')[-1][:-10]
            if 'name="jschl_vc"' in row:
                jschlVc = row.split('value="')[-1][:-3]
            if 'name="pass"' in row:
                passValue = row.split('value="')[-1][:-3]
        jschlAnswer = cls._getAnswer(html)
        if s and jschlVc and passValue and jschlAnswer:
            return {
                "s": s,
                "jschl_vc": jschlVc,
                "pass": passValue,
                "jschl_answer": str(jschlAnswer)
            }
        return None
    

    @classmethod
    def _getCookies(cls):
        '''
        get a session has cookies
        :return:
        '''
        session = requests.Session()
        session.headers.update(cls._headers)
        # get information from 503 page
        first = session.get("https://hidemyna.me/en/proxy-list/", allow_redirects=False)
        cookies1 = first.cookies.get_dict()
        # crack requests arguments
        params = cls._getRequestParams(first.text)
        # Must wait 4 seconds here
        time.sleep(4)
        second = session.get("https://hidemyna.me/cdn-cgi/l/chk_jschl", params=params, allow_redirects=False)
        cookies2 = second.cookies.get_dict()
        # set cookies dictionary
        returnCookies = {}
        returnCookies.update(cookies1)
        returnCookies.update(cookies2)
        return returnCookies
    
    
if __name__ == '__main__':
    # Hidemyna.start()
    Hidemyna.start()