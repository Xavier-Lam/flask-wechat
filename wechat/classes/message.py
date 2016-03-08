#encoding:utf8

from .base import WeChatMessageBase

class WeChatMessage(WeChatMessageBase):
    _allowed_keys = dict(WeChatMessageBase._allowed_keys, **dict(
        MsgId=int,
        Content=str,
        PicUrl=str,
        MediaId=int,
    ))