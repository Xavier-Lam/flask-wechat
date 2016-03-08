#encoding:utf8

from . import WeChatMessageBase, WeChatResponse

class WeChatRequest(WeChatMessageBase):
    def reply_text(self, value):
        return self.reply("text", value)

    def reply(self, type, value):
        return WeChatResponse(msgtype=type, content=value)