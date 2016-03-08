#encoding:utf8

import time
from xml.etree import ElementTree

__all__ = ["WeChatEvent", "WeChatMessage", "WeChatMessageBase", "WeChatRequest",
    "WeChatResponse"]

class WeChatMessageBase(object):
    _allowed_keys = dict(
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
        allowed = self._allowed_keys
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
            from . import WeChatEvent
            message = WeChatEvent(**params)
        else:
            from . import WeChatMessage
            message = WeChatMessage(**params)
        return message

from .event import WeChatEvent
from .message import WeChatMessage
from .request import WeChatRequest
from .response import WeChatResponse