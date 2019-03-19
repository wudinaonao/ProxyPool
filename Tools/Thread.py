import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

import threading


class Thread(threading.Thread):

    # create a thread
    
    def __init__(self, threadName, spider):
        super().__init__()
        self.name = threadName
        self.spider = spider

    def run(self):
        self.spider.start()