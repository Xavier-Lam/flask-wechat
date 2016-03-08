#encoding:utf8

import requests
from . import wechat_blueprint as wechat
from .httpclient import WeChatHTTPClient

class WeChatClient(object):
    def __init__(self, identity):
        self.__access_token = None
        self.expire_in = 0
        self.identity = identity
        config = wechat.core.get_config(identity)
        
    @property
    def access_token(self):
        return self.__access_token
        
    # def refresh_access_token(self):
    #     params = dict(
    #         grant_type="client_credential",
    #         appid=appid,
    #         secret=appsecret
    #     )
    #     client = WeChatHTTPClient(self.identity)
    #     resp = requests.get("https://api.weixin.qq.com/cgi-bin/token", 
    #         params=params)
    #     if resp.status_code == requests.codes.ok:
    #         resp = resp.json()
    #         self.__access_token = resp["access_token"]
    #         self.expire_in = resp["expires_in"]
    #     return self.access_token, self.expire_in
        
    def get_menus(self):
        client = WeChatHTTPClient(self.identity)
        resp, err = client.get("/cgi-bin/get_current_selfmenu_info")
        return {} if err else resp.json().get("selfmenu_info")

    def get_medias(self, type="", skip=0, take=30):
        pass
        
    def add_media(type, content, temporary=False):
        client = WeChatHTTPClient(self.identity)
        files = dict(
            type=type,
            media=("filename", content, "mimetype")
        )
        resp, err = client.post("/cgi-bin/material/add_material", files=files)
        return 0 if err else resp.json().get("media_id") or 0