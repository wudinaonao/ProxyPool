import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

import re
import json
import requests
from datetime import datetime
import hashlib
from Tools.Log import Log as logger
from DataBase.DBUtil import DBUtil


class GeneralTool():
    
    # instances database
    _database = DBUtil()
    
    @staticmethod
    def isIPAddress(ip):
        patterns = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if patterns.match(ip.strip()):
            return True
        return False

    @staticmethod
    def _isProxyType(type):
        if type:
            if type.strip().lower() == "http" or type.strip().lower() == "https":
                return True
        return False
    
    @staticmethod
    def _isPort(port):
        if port:
            try:
                port = int(port.strip())
                if 0 < port < 65535:
                    return True
            except:
                return False
        return False
    
    @staticmethod
    def checkPortOrType(key, value):
        '''
        check port or type is specification
        :param key:
        :param value:
        :return:
        '''
        if key == "port":
            if not GeneralTool._isPort(value):
                return "80"
            else:
                return value
        if key == "type":
            if not GeneralTool._isProxyType(value):
                return "HTTP"
            else:
                return value
    
    @classmethod
    def wirteToDataBase(cls, proxyDictList):
        if not proxyDictList:
            return None
        try:
            logger.info("UnVerified table that writing proxy to the database ...")
            for proxyDict in proxyDictList:
                result = cls._database.queryIsExist("UnVerified", {"md5": proxyDict['md5']})
                if not result:
                    logger.info("writing to unverified tabel ---> IP: {0: <18}Port:{1: <8}Type:{2: <8}Location:{3}".format(proxyDict['ip'],
                                                                                                                            proxyDict['port'],
                                                                                                                            proxyDict['type'],
                                                                                                                            proxyDict['location']),
                                level="ALL")
                    cls._database.insert("UnVerified", proxyDict)
        except Exception:
            logger.error("An error occurred in the function ---> wirteToDataBase")
            return None
            
            
    @staticmethod
    def getIpLocation(ip):
        logger.info("querying loaction of {0}".format(ip), level="DETAILED")
        try:
            url = "http://ip.taobao.com/service/getIpInfo.php?ip=" + ip
            res = requests.get(url, timeout=5)
            res = json.loads(res.content)
            if res['code'] == 0:
                if res['data']['country'] == "XX": res['data']['country'] = ""
                if res['data']['area'] == "XX": res['data']['area'] = ""
                if res['data']['region'] == "XX": res['data']['region'] = ""
                if res['data']['city'] == "XX": res['data']['city'] = ""
                if res['data']['isp'] == "XX": res['data']['isp'] = ""
                location = "{0} {1} {2} {3} {4}".format(res['data']['country'],
                                                        res['data']['area'],
                                                        res['data']['region'],
                                                        res['data']['city'],
                                                        res['data']['isp'])
                if location.strip():
                    return location
            return "Unknown Location"
        except Exception:
            logger.error("an error occurred while querying to location of ip [{0}]".format(ip))
            return "Unknown Location"
    
    @staticmethod
    def formatDate():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def computeMD5(ip, port, type):
        string = ip.lower() + port.lower() + type.lower()
        hl = hashlib.md5()
        hl.update(string.encode(encoding='utf-8'))
        return hl.hexdigest().upper()
    
    @staticmethod
    def splitList(inputList, size=100):
        '''
        input a list, split the list to size
        example:
                input list ---> [1, 2, 3, 4, 5, 6, 7] size = 2
                return list --> [[1, 2], [3, 4], [5, 6], [7]]
                
        :param inputList:
        :param size:
        :return:
        '''
        return [inputList[i:i + size] for i in range(0, len(inputList), size)]
        
    @staticmethod
    def computePercentage(value, max):
        '''
        :param value:   float type
        :param max:     float type
        :return:    a string exampe 25.35%
        '''
        return str(round((float(value) / float(max)), 4) * 100)[:5] + "%"
    
    @staticmethod
    def getDataBaseObject():
        return DBUtil()
    
if __name__ == '__main__':
    # for i in range(20):
    #     print(GeneralTool.getIpLocation("151.21.135.54"))
    # print(GeneralTool.checkPortOrType("port", "65534"))
    # print(GeneralTool.splitList([1, 2, 3, 4, 5, 6, 7], 2))
    print(GeneralTool.computePercentage(1200, 890))