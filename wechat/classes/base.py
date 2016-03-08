#encoding:utf8

import time
from xml.etree import ElementTree

def _patch():
    def CDATA(text=None):
        element = ElementTree.Element("![CDATA[")
        element.text = text
        return element

    ElementTree.CDATA = CDATA

    ElementTree._original_serialize_xml = ElementTree._serialize_xml
    def _serialize_xml(write, elem, qnames, namespaces, *args, **kwargs):
        if elem.tag == "![CDATA[":
            write("\n<%s%s]]>\n" % (
                    elem.tag, elem.text))
            return
        return ElementTree._original_serialize_xml(
            write, elem, qnames, namespaces, *args, **kwargs)
    ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml

_patch()

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

        # d = { key: getattr(self, key.lower()) 
        #     for key in allowed 
        #     if hasattr(self, key.lower()) 
        #     and isinstance(getattr(self, key.lower()), allowed[key]) }

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