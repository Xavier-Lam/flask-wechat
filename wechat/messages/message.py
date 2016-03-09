#encoding:utf8

from . import WeChatRequest

class WeChatMessage(WeChatRequest):
    _allowed_keys = dict(WeChatRequest._allowed_keys, **dict(
        MsgId=int,
        Content=str,
        PicUrl=str,
        MediaId=int,
    ))