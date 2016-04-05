#encoding:utf8

from . import WeChatRequest

class WeChatMessage(WeChatRequest):
    __fields__ = dict(WeChatRequest.__fields__, **dict(
        MsgId=int,
        MsgType=str,
        Content=str,
        PicUrl=str,
        MediaId=str,
        Format=str,
        Recognition=str,
        ThumbMediaId=str,
        Location_X=float,
        Location_Y=float,
        Scale=int,
        Label=str,
        Title=str,
        Description=str,
        Url=str
    ))
    
    def __init__(self, **kwargs):
        if "msgid" not in kwargs or "msgtype" not in kwargs:
            raise ValueError("message must contains msgid")
        super(WeChatMessage, self).__init__(**kwargs)
        
    def __repr__(self):
        return "<%s %s:%s>"%(self.__class__.__name__, self.msgtype, self.msgid)