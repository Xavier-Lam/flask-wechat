#encoding:utf8

from . import WeChatMessageBase, WeChatResponse

class WeChatRequest(WeChatMessageBase):
    """A request comes from WeChat
    
    When received a request from wechat server, Flask-WeChat will create a
    WeChatEvent or WeChatMessage instance which inherit from this class.
    """
    
    def reply_text(self, value):
        """A short cut to reply a text message
        
        :param value: text you want to reply.
        
        :returns :class:`flask_wechat.messages.WeChatResponse`
        """
        return self.reply("text", content=value)
        
    def reply_media(self, type, media_id, **kwargs):
        """A short cut to reply media message.
        
        This method can create a media WeChatResponse class automaticly.
        Including image/voice/video
        
        :param type: media type including image/voice/video
        :param media_id: the media_id of the media
        :param \*\*kwargs: additional reply information like title or 
                           description of the reply video
        
        :returns :class:`flask_wechat.messages.WeChatResponse`
        """
        assert type in ["image", "voice", "video"]
        media = kwargs or {}
        media["mediaid"] = media_id
        return self.reply(type, **{type: media})
        
    def reply_article(self, articles):
        """A short cut to reply articles
        
        :param articles: a list of article or a article dict
        """
        if isinstance(articles, dict):
            articles = [articles]
        return self.reply("news", articlecount=len(articles), articles=articles)

    def reply(self, type, **kwargs):
        """A short cut to reply a message
        
        :param type: the message type that you want to reply
        :param \*\*kwargs: message keypairs except fromusername/tousername/
                           createtime
        
        :returns :class:`flask_wechat.messages.WeChatResponse`
        """
        return WeChatResponse(msgtype=type, fromusername=self.tousername, 
            tousername=self.fromusername, **kwargs)