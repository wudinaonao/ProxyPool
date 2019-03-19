import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

from Tools.Thread import Thread
from Test.ProxyTest import ProxyTest
from Tools.Log import Log as logger
from Tools.GeneralTool import GeneralTool


class Scheduler():
    
    _database = GeneralTool.getDataBaseObject()
    
    
    @classmethod
    def start(cls):
        '''
        start project
        :return:
        '''
        while True:
            logger.info("start crawing proxy ...")
            cls.craw()
            logger.info("start testing proxy ...")
            cls.test()
            logger.info("current task finish")
        
    @classmethod
    def craw(cls):
        '''
        craw proxy method
        :return:
        '''
        try:
            threadObjectList = []
            # search spider in Spider dir
            for spiderName in cls._spiderModuleList():
                moduleName = 'Spider.' + str(spiderName)
                # Dynamic import spider module
                spiderModule = __import__(name=moduleName,
                                          fromlist=[str(spiderName)])
                # get spider class
                spiderClass = getattr(spiderModule, str(spiderName))
                # create spider instarnces and start thread for grab proxy
                createThread = Thread(str(spiderName), spiderClass())
                createThread.start()
                # join thread object to list
                threadObjectList.append(createThread)
        # use to thread object join method, otherwise it will not wait for all
        # grab proxy threads to be completed, and proceed directly to the next
        # step
        #
        # if crawling and testing are done separately, not following code is
        # not used
        
        # for threadObject in threadObjectList:
        #     threadObject.join()
        except Exception:
            logger.error("An error occurred in the craw function of scheduler class")
        
    
    @classmethod
    def test(cls):
        '''
        test proxy method
        :return:
        '''
        # try:
        # get proxy test list from UnVerified table
        proxyDictList = cls._database.query("UnVerified")
        logger.info("Start test proxy from table UnVerified... proxy count ---> " + str(len(proxyDictList)))
        ProxyTest.testConcurrent(proxyDictList)
        # get proxy test list from Verified table
        proxyDictList = cls._database.query("Verified")
        logger.info("Start test proxy from table Verified... proxy count ---> " + str(len(proxyDictList)))
        ProxyTest.testConcurrent(proxyDictList)
        # except Exception:
        #     logger.error("An error occurred in the Test function of scheduler class")
       
    @classmethod
    def _spiderModuleList(cls):
        '''
        get spider module name list from Spider dir
        :return:
        '''
        spiderList = []
        spiderDir = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "Spider")
        for spiderName in os.listdir(spiderDir):
            if not "__" in spiderName:
                spiderList.append(spiderName.split(".")[0])
        return spiderList
        
if __name__ == '__main__':
    
    # start spider and test proxy
    # this is main
    Scheduler.start()
    