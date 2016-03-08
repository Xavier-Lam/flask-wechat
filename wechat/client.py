#encoding:utf8

import requests
from .message import Message

class WeChatClient(object):
    def __init__(self, appid):
        self.__access_token = None
        self.expire_in = 0
        
    def get_config(self):
        return dict(
            appid=self.appid,
            app_secret=self.app_secret,
            token=self.token,
        )
        
    @property
    def access_token(self):
        return self.__access_token
        
    def refresh_access_token(self):
        params = dict(
            grant_type="client_credential",
            appid=appid,
            secret=appsecret
        )
        resp = requests.get("https://api.weixin.qq.com/cgi-bin/token", 
            params=params)
        if resp.status_code == requests.codes.ok:
            resp = resp.json()
            self.__access_token = resp["access_token"]
            self.expire_in = resp["expires_in"]
        return self.access_token, self.expire_in
        
    def get_menus(self):
        rv = {}
        resp = requests.get("https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info",
            params={"access_token": self.access_token})
        if resp.status_code == requests.codes.ok:
            rv = resp.json().get("selfmenu_info")
        return rv

    def get_medias(self, type="", skip=0, take=30):
        pass

    def reply(self, message):
        if not isinstance(message, Message):
            message = Message.deserialize(message)
        if not message:
            return None
        return Message(fromusername=self.appid, tousername=message.fromusername,
            msgtype="text", content="hello world!")