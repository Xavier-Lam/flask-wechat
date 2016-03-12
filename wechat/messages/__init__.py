#encoding:utf8

import time
from xml.etree import ElementTree

__all__ = ["WeChatEvent", "WeChatMessage", "WeChatMessageBase", "WeChatRequest",
    "WeChatResponse"]

class WeChatMessageBase(object):
    __slots__ = dict(
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
        
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)
        
    def serialize(self):
        allowed = self.__slots__
        d = dict()
        for key in allowed:
            if hasattr(self, key.lower()):
                value = getattr(self, key.lower())
                if value and isinstance(value, allowed[key]):
                    d[key] = value

        root = ElementTree.Element("xml")
        for key, value in d.items():
            ele = ElementTree.SubElement(root, key)
            if isinstance(value, str):
                ele.append(ElementTree.CDATA(value))
            else:
                ele.text = value
        rv = ElementTree.tostring(root, "unicode", "xml")
        return rv

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
        if params["msgtype"] == "event":
            message = WeChatEvent(**params)
        else:
            message = WeChatMessage(**params)
        return message
        
    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
            
    def items(self):
        for key in self.__slots__:
            if hasattr(self, key):
                yield (key, getattr(self, key))
            
    def __getitem__(self, key):
        return getattr(self, key)
        
    def __setitem__(self, key, value):
        setattr(self, key, value)
        
    def __iter__(self):
        for key in self.__slots__:
            if hasattr(self, key):
                yield key
        
    def __str__(self):
        return self.serialize()
        
    def __repr__(self):
        return "<%s %s>"%(self.__class__.__name__, self.msgtype)

from .response import WeChatResponse
from .request import WeChatRequest
from .event import WeChatEvent
from .message import WeChatMessage