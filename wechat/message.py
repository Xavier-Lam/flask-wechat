#encoding:utf8

import re
import time
from xml.etree import ElementTree

def create_node(nodename, value):
    return "<{nodename}><![CDATA[{value}]]></{nodename}>"\
        .format(nodename=nodename, value=value)

class WeChatMessage(object):
    def __init__(self, fromusername="", tousername="", msgtype="", content="", createtime=0,
        msgid=None, **kwargs):
        self.fromusername = fromusername
        self.tousername = tousername
        self.createtime = createtime or time.time()
        self.msgtype = msgtype
        self.content = content
        self.msgid = msgid
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)
        
    @staticmethod
    def deserialize(self, string):
        try:
            tree = ElementTree.fromstring(string)
        except:
            return None
        params = {}
        children = tree.getchildren()
        for child in children:
            if child.items:
                pass
            else:
                params[child.tag.lower()] = child.text
        message = WeChatMessage(**params)
        return message

    def serialize(self):
        nodelist = []
        nodelist.push(create_node("ToUserName", self.tousername))
        nodelist.push(create_node("FromUserName", self.fromusername))
        nodelist.push(create_node("CreateTime", self.createtime))
        nodelist.push(create_node("MsgType", self.msgtype))
        if self.content:
            nodelist.push(create_node("Content", self.content))
        if self.msgid:
            nodelist.push(create_node("MsgId", self.msgid))
        if hasattr(self, "picurl"):
            nodelist.push(create_node("PicUrl", self.picurl))
        if hasattr(self, "mediaid"):
            nodelist.push(create_node("MediaId", self.mediaid))
        if hasattr(self, "format"):
            nodelist.push(create_node("Format", self.format))
        if hasattr(self, "thumbmediaid"):
            nodelist.push(create_node("ThumbMediaId", self.thumbmediaid))
            
        return create_node("xml", "".join(nodelist))