#encoding:utf8

import requests
from . import wechat_blueprint as wechat
from .httpclient import WeChatHTTPClient

class WeChatClient(object):
    def __init__(self, identity):
        self.__access_token = None
        self.expire_in = 0
        self.identity = identity
        config = wechat.core._get_config(identity)
        
    @property
    def access_token(self):
        return self.__access_token
        
    def get_menus(self):
        client = WeChatHTTPClient(self.identity)
        resp, err = client.get("/get_current_selfmenu_info")
        return {} if err else resp.get("selfmenu_info")

    def get_medias(self, type="", skip=0, take=30):
        pass
        
    def add_media(self, type, content, temporary=False):
        client = WeChatHTTPClient(self.identity)
        files = dict(
            type=type,
            media=("filename", content, "mimetype")
        )
        resp, err = client.post("/material/add_material", files=files)
        return 0 if err else resp.get("media_id") or 0

    def get_users(self, next_openid=""):
        client = WeChatHTTPClient(self.identity)
        resp, err = client.post("/user/get")
        return {} if err else resp