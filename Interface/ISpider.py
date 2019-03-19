import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

from abc import ABCMeta, abstractmethod


class ISpider(metaclass=ABCMeta):
    
    @classmethod
    @abstractmethod
    def start(cls):
        pass
    
    @classmethod
    @abstractmethod
    def _getHtml(cls):
        pass
    
    @classmethod
    @abstractmethod
    def _getProxyResultList(cls, html):
        pass
    
