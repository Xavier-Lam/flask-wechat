#encoding:utf8

import time
from . import WeChatMessageBase
from .subelement import SubElement, SubList

class WeChatResponse(WeChatMessageBase):
    """A response to wechat
    
    Handlers return a WeChatResponse instance.
    
    :param \*\*kwargs: keyword arguments passed on to the response.
                       keys can be any key to lowercase in __fields__,
                       and must contains msgtype.
    """

    __fields__ = dict(WeChatMessageBase.__fields__, **dict(
        MsgType=str,
        Content=str,
        Image=SubElement(
            MediaId=str
        ),
        Voice=SubElement(
            MediaId=str
        ),
        Video=SubElement(
            MediaId=str,
            Title=str,
            Description=str,
        ),
        Music=SubElement(
            Title=str,
            Description=str,
            MusicURL=str,
            HQMusicURL=str,
            ThumbMediaId=str,
        ),
        ArticleCount=int,
        Articles=SubList("item", dict(
            Title=str,
            Description=str,
            PicUrl=str,
            Url=str
        ))
    ))
    
    def __init__(self, **kwargs):
        if "msgtype" not in kwargs:
            raise ValueError("response must contains a msgtype")
        if "createtime" not in kwargs:
            kwargs["createtime"] = int(time.time())
        super(WeChatResponse, self).__init__(**kwargs)