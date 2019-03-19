import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])
import grequests
from bs4 import BeautifulSoup as bs
from Tools.Log import Log as logger
import requests
from datetime import datetime
from Tools.GeneralTool import GeneralTool


class ProxyTest():
    
    _database = GeneralTool.getDataBaseObject()
    
    # test time out unit seconds
    _timeOut = 10
    # test site
    _testSiteUrl = "http://www.baidu.com"
    _testSSLSiteUrl = "https://www.baidu.com"
    # test site title
    _testSiteTitle = "百度一下，你就知道"
    # concurrent count
    _coucurrentCount = 100
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
 
    @classmethod
    def testConcurrent(cls, proxyDictList):
        '''
        concurrent mode test proxy
        examlpe:
            proxyDictList = [
                                {"id":"1", "ip":"8.8.8.8", ...},
                                ...
                            ]
        :param proxyDictList:
        :return:
        '''
        # get test list, content is proxy information dictionary list
        # example:
        #             [[1, 2], [3, 4], ...]
        #
        taskListList = GeneralTool.splitList(proxyDictList, size=cls._coucurrentCount)
        proxyDictList = GeneralTool.splitList(proxyDictList, size=cls._coucurrentCount)
        # return None if task list is empty
        if taskListList == []:
            return None
        # start conccurent test
        logger.info("testing proxy concurrent count --> %s" % cls._coucurrentCount)
        for j, taskList in enumerate(taskListList):
            if taskList == []:
                continue
            resultList = grequests.map(cls._loadTaskList(taskList), size=cls._coucurrentCount, gtimeout=60)
            # test resutl
            for i, result in enumerate(resultList):
                # update check date
                proxyDictList[j][i]['lastUpdateTime'] = cls._formatDate()
                # return html and status code equal 200
                if result is not None and result.status_code == 200:
                    result.encoding = "utf-8"
                    proxyDictList[j][i]['speed'] = str(round(result.elapsed.microseconds / 1000000, 2)) + "s"
                    # html is test site html
                    if cls._isSuccessOpenSite(result.text):
                        # success callback
                        cls._success(proxyDictList[j][i])
                    else:
                        # failed callback
                        cls._failed(proxyDictList[j][i])
                else:
                    # failed callback
                    cls._failed(proxyDictList[j][i])
            logger.info("testing progress is {0}".format(GeneralTool.computePercentage(j + 1, len(taskListList))))
        logger.info("delete invaild proxy  ......")
        cls._deleteInVailed()
        logger.info("test completed")
        return None
        
    @classmethod
    def _loadTaskList(cls, proxyDictList):
        '''
        make grequests task list
        
        :param proxyDictList:
        :return:
        '''
        taskList = []
        for proxyDict in proxyDictList:
            if proxyDict["type"].lower().strip() == "https":
                ip = proxyDict["ip"].lower().strip()
                port = proxyDict["port"].lower().strip()
                proxies = {
                    "https": "https://" + ip + ":" + port,
                }
                taskList.append(grequests.get(cls._testSSLSiteUrl,
                                              headers=cls.headers,
                                              proxies=proxies,
                                              timeout=cls._timeOut))
            else:
                ip = proxyDict["ip"].lower().strip()
                port = proxyDict["port"].lower().strip()
                proxies = {
                    "http": "http://" + ip + ":" + port,
                }
                taskList.append(grequests.get(cls._testSiteUrl,
                                              headers=cls.headers,
                                              proxies=proxies,
                                              timeout=cls._timeOut))
        return taskList
    
    @classmethod
    def _failed(cls, proxyDict):
        '''
        test failed callback
        :return:
        '''
        md5 = proxyDict["md5"]
        # check has this proxy in the Verified table
        # have update or not insert
        logger.error("Invaild Proxy ---> IP: {0: <18}PORT: {1: <8}TYPE: {2: <8}"
                     .format(proxyDict['ip'], proxyDict['port'], proxyDict['type']), level="DETAILED")
        
        if cls._database.queryIsExist("Verified", {"md5": proxyDict['md5']}):
            # get IP weight by Verified table, if IP in the Verified table
            weight = cls._database.query("Verified", {'md5': md5})[0]['weight']
            info = {
                "key_values": {
                    "weight": weight,
                    "speed": proxyDict["speed"],
                    "lastUpdateTime": proxyDict["lastUpdateTime"]
                },
                "postions": {"md5": md5}
            }
            cls._database.update(tableName="Verified", info=info)
        cls._clearUnVerifiedRow(proxyDict)
        return True
    
    @classmethod
    def _success(cls, proxyDict):
        '''
        test success callback
        :return:
        '''
        md5 = proxyDict["md5"]
        # check has this proxy in the Verified table
        # have update or not insert
        logger.info("Success Proxy ---> IP: {0: <18}PORT: {1: <8}TYPE: {2: <8}"
                     .format(proxyDict['ip'], proxyDict['port'], proxyDict['type']), level="DETAILED")
        if cls._database.queryIsExist("Verified", {"md5": proxyDict['md5']}):
            # get IP weight by Verified table, if IP in the Verified table
            weight = cls._database.query("Verified", {'md5': md5})[0]['weight']
            weight += 1
            info = {
                "key_values": {
                    "weight": weight,
                    "speed": proxyDict["speed"],
                    "lastUpdateTime": proxyDict["lastUpdateTime"]
                },
                "postions": {"md5": md5}
            }
            if cls._database.update(tableName="Verified", info=info):
                return True
        else:
            # insert up IP to Verified table if not in Verified table
            proxyDict['id'] = "null"
            proxyDict['weight'] += 1
            if cls._database.insert(tableName="Verified", info=proxyDict):
                return True
        cls._clearUnVerifiedRow(proxyDict)
        return False

    
    
    @classmethod
    def _isSuccessOpenSite(cls, html):
        '''
        Determine if have open the target site
        maybe this method can be package into a class
        :param html:
        :return:
        '''
        # parser html
        soup = bs(html, "lxml")
        if soup.title is None:
            return False
        if soup.title.text.strip() == cls._testSiteTitle:
            return True
        return False
    
    @classmethod
    def _deleteInVailed(cls):
        '''
        delete invailde proxy in the UnVerified tabel and Verified tabel
        :return:
        '''
        # clean UnVerified table
        # cls._database.delete("UnVerified")
        # if row weight less than 0 in the Verified table, delete it
        proxyDictList = cls._database.query("Verified")
        for proxyDict in proxyDictList:
            if proxyDict['weight'] < 0:
                cls._database.delete("Verified", {"md5": proxyDict['md5']})

    @classmethod
    def _clearUnVerifiedRow(cls, proxyDict):
        '''

        :param proxyDict:
        :return:
        '''
        if cls._database.queryIsExist("UnVerified", {"md5": proxyDict['md5']}):
            cls._database.delete("UnVerified", {"md5": proxyDict['md5']})

    @classmethod
    def _formatDate(cls):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
if __name__ == '__main__':

    pass
