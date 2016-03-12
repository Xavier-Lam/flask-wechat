#encoding:utf8

from . import WeChatMessageBase

class WeChatResponse(WeChatMessageBase):
    __slots__ = dict(WeChatMessageBase.__slots__, **dict(
        MsgId=int,
        Content=str,
        PicUrl=str,
        MediaId=int,
    ))