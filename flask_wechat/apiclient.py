#encoding:utf8

import json, sys

import requests
from . import wechat_blueprint as wechat
from .signals import wechat_granted, wechat_error, wechat_servererror

__python_version__ = sys.version[0]

__all__ = ["WeChatApiClient"]

class WeChatApiClient(object):
    __baseaddr__ = "https://api.weixin.qq.com"
    __prefix__ = "/cgi-bin"

    __accesstoken = None

    def __init__(self, identity):
        self.__accesstoken = wechat.core._accesstoken_maintainer(identity)
        self.identity = identity

    def get(self, url, **kwargs):
        kwargs["method"] = "get"
        kwargs = self._handlekwargs(url, kwargs)
        resp = self.requests(**kwargs)
        return self._onresponse(resp)
        
    def get_raw(self, url, **kwargs):
        kwargs["method"] = "get"
        kwargs = self._handlekwargs(url, kwargs)
        return self.requests(**kwargs)
        
    def post(self, url, **kwargs):
        kwargs["method"] = "post"
        kwargs = self._handlekwargs(url, kwargs)
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
        try:
            json = resp.json()
            code = json.get("errcode")
            if code:
                self.__send_signal(wechat_error, resp, code=code)
            else:
                self.__accesstoken = json["access_token"]
                # 更新外部token
                expires_in = json.get("expires_in") or 7200
                self.__update_accesstoken(self.__accesstoken, expires_in)
                self.__send_signal(wechat_granted, resp, 
                    accesstoken=self.__accesstoken, expires_in=expires_in)
        except Exception as e:
            self.__send_signal(wechat_servererror, resp, exception=e)
        return self.__accesstoken

    def requests(self, method, url, *args, **kwargs):
        url = self.__baseaddr__.rstrip("/") + self.__prefix__ + url
        if "json" in kwargs:
            # 解决中文被转码问题
            headers = kwargs.get("headers") or {}
            headers["Content-Type"] = "application/json; charset=UTF-8"
            headers["Encoding"] = "utf-8"
            kwargs["headers"] = headers
            kwargs["data"] = json.dumps(kwargs["json"], ensure_ascii=False)
            if __python_version__ == "3":
                kwargs["data"] = kwargs["data"].encode("utf-8")
            del kwargs["json"]
        return getattr(requests, method)(url, *args, **kwargs)

    @property
    def accesstoken(self):
        token = self.__accesstoken
        if token:
            return token
        else:
            return self.grant()

    def _onresponse(self, resp):
        """处理一般返回"""
        try:
            json = resp.json()
            code = json.get("errcode") or 0
            rv = (json, code)
            if code:
                # 处理异常
                self.__send_signal(wechat_error, resp, code=code)
                resp = self._handleerror(json, code)
                if resp:
                    json = resp.json()
                    code = json.get("errcode") or 0
                    if code:
                        self.__send_signal(wechat_error, resp, code=code)
                    else:
                        # 成功处理
                        rv = (json, code)
            return rv
        except Exception as e:
            self.__send_signal(wechat_servererror, resp, exception=e)
            return {}, -2

    def _handleerror(self, resp_json, code):
        """在返回异常后再次请求"""
        if code in [40001, 40014, 42001, 42007]:
            # accesstoken 失效
            self.grant()
            self.__lastrequest["params"]["access_token"] = self.accesstoken
            return self.requests(**self.__lastrequest)
        else:
            pass
            
    def _handlekwargs(self, url, kwargs):
        kwargs["url"] = url
        params = kwargs.get("params") or {}
        params["access_token"] = self.accesstoken
        kwargs["params"] = params
        self.__lastrequest = kwargs
        return kwargs
            
    def __send_signal(self, signal, resp, **kwargs):
        signal.send(wechat.core, identity=self.identity, response=resp, **kwargs)
        
    def __update_accesstoken(self, value, expires_in=None):
        kwargs = {"expires_in": expires_in} if expires_in else {}
        return wechat.core._accesstoken_maintainer(self.identity, value, 
            **kwargs)