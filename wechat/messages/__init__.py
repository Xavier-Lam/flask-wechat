#encoding:utf8

import time
from xml.etree import ElementTree

__all__ = ["WeChatEvent", "WeChatMessage", "WeChatMessageBase", "WeChatRequest",
    "WeChatResponse"]
    
class XMLElementBase(object):
    __fields__ = dict()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = WeChatResponseSubList(value)
            elif isinstance(value, dict):
                value = WeChatResponseSubElement(value)
            elif isinstance(value, str):
                value = value.strip()
            setattr(self, key.lower(), value)

    def serialize(self, parent=None, return_=True):
        d = dict()
        for key in self.__fields__:
            if hasattr(self, key.lower()):
                value = getattr(self, key.lower())
                if value!=None and isinstance(value, self.__fields__[key]):
                    d[key] = value
                    
        if not parent:
            parent = ElementTree.Element("xml")
        for key, value in d.items():
            ele = ElementTree.SubElement(parent, key)
            if isinstance(value, str):
                ele.append(ElementTree.CDATA(value))
            elif isinstance(value, WeChatResponseSubElement):
                value.serialize(ele, False)
            elif isinstance(value, WeChatResponseSubList):
                value.serialize(ele, False)
            else:
                ele.text = str(value)
        if return_:
            return ElementTree.tostring(parent, "unicode", "xml")
           
    @staticmethod
    def deserialize(string):
        try:
            tree = ElementTree.fromstring(string)
        except:
            return None
        params = {}
        for child in tree:
            if child.items():
                pass
            else:
                params[child.tag.lower()] = child.text
        if params["msgtype"].strip() == "event":
            message = WeChatEvent(**params)
        else:
            message = WeChatMessage(**params)
        return message
        
    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
            
    def items(self):
        for key in self.__fields__:
            if hasattr(self, key):
                yield (key, getattr(self, key))
            
    def __getitem__(self, key):
        return getattr(self, key)
        
    def __setitem__(self, key, value):
        setattr(self, key, value)
        
    def __iter__(self):
        for key in self.__fields__:
            if hasattr(self, key):
                yield key
        
    def __str__(self):
        return self.serialize()
        

class WeChatMessageBase(XMLElementBase):
    __fields__ = dict(
        ToUserName=str,
        FromUserName=str,
        CreateTime=int,
        MsgType=str,
    )

    def __init__(self, **kwargs):
        self.createtime = kwargs.get("createtime") or time.time
        self.fromusername = kwargs.get("fromusername")
        self.tousername = kwargs.get("tousername")
        self.msgtype = kwargs.get("msgtype")
        
        super(WeChatMessageBase, self).__init__(**kwargs)
        
    def __repr__(self):
        return "<%s %s>"%(self.__class__.__name__, self.msgtype)

from .response import WeChatResponse
from .request import WeChatRequest
from .event import WeChatEvent
from .message import WeChatMessage
from .subelement import WeChatResponseSubElement, WeChatResponseSubList