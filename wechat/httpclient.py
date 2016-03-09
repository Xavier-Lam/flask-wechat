#encoding:utf8

import requests
from . import wechat_blueprint as wechat
from .signals import wechat_error, wechat_servererror

__all__ = ["WeChatHTTPClient"]

class WeChatHTTPClient(object):
    __baseaddr__ = "https://api.weixin.qq.com/cgi-bin"

    __accesstoken = None

    def __init__(self, identity):
        self.__accesstoken = wechat.core._accesstoken_maintainer(identity)
        self.identity = identity

    def get(self, url, **kwargs):
        kwargs["method"] = "get"
        kwargs["url"] = url
        params = kwargs.get("params") or {}
        params["access_token"] = self.accesstoken
        kwargs["params"] = params
        self.__lastrequest = kwargs
        resp = self.requests(**kwargs)
        return self._onresponse(resp)
        
    def post(self, url, **kwargs):
        kwargs["method"] = "post"
        kwargs["url"] = url
        params = kwargs.get("params") or {}
        params["access_token"] = self.accesstoken
        kwargs["params"] = params
        self.__lastrequest = kwargs
        resp = self.requests(**kwargs)
        return self._onresponse(resp)
        
    def grant(self):
        params = dict(
            grant_type="client_credential",
            appid=wechat.core._get_config(self.identity).get("appid"),
            secret=wechat.core._get_config(self.identity).get("appsecret")
        )
        resp = self.requests("get", "/token", 
            params=params)
        if resp.status_code == requests.codes.ok:
            resp = resp.json()
            self.__accesstoken = resp["access_token"]
            # 更新外部token
            wechat.core._accesstoken_maintainer(self.identity, self.__accesstoken)
        return self.__accesstoken

    def requests(self, method, url, *args, **kwargs):
        url = self.__baseaddr__ + url
        return getattr(requests, method)(url, *args, **kwargs)

    @property
    def accesstoken(self):
        token = self.__accesstoken
        if token:
            return token
        else:
            return self.grant()

    def _onresponse(self, resp):
        try:
            if resp.status_code == requests.codes.ok:
                return resp.json(), 0
            else:
                json = self._handleerror(resp).json()
                return json, json.get("errcode") or 0
        except:
            return {}, -2

    def _handleerror(self, resp):
        try:
            json = resp.json()
            code = json["errcode"]
        except (KeyError, ValueError) as e:
            wechat_servererror.send(self, resp)
            return resp, -2
        else:
            wechat_error.send(self, resp.status_code, code, resp)
        if code==42001 or code==42007 or code==40014:
            # accesstoken 失效
            self.grant()
            return self.requests(**self.__lastrequest)
        else:
            return resp, code