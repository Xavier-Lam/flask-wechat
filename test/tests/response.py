#encoding:utf8

import re

from . import ClientTest
from ..app import app, wechat
from .. import requests 

class ResponseTestCases(ClientTest):
    token = "token"
    pattern = r"^<xml>(?:\s*<([a-zA-Z0-9_]+)>.*?</\1>)+\s*</xml>$"
        
    def setUp(self):
        super(ResponseTestCases, self).setUp()
        app.config["id"] = self.identity
        app.config["token"] = self.token
        # app.config["WECHAT_DEBUG"] = True
        # app.config["DEBUG"] = True
        self.app = app.test_client()
        wechat.init_app(app)
        self.posturl = wechat.callback_prefix +  "/" + self.identity + "/"
        
    def test_1_verify(self):
        echostr = "aaaaaa"
        url = self.posturl + self._query_str + "&echostr=" + echostr
        resp = self.app.get(url)
        self.assertTrue(resp.data.decode("utf8")==echostr)
        self.__response_match(resp, xml=False)
        
    def test_2_request(self):
        resp = self.create_request(requests.subscribe)
        self.__response_match(resp, contains="welcome")
        # 图片
        resp = self.create_request(requests.image)
        self.__response_match(resp, contains="image")
        
    def test_3_text(self):
        resp = self.create_request(requests.text_ddd)
        self.__response_match(resp, contains="in")
        
        resp = self.create_request(requests.text_aaab)
        self.__response_match(resp, contains="bbb")
        self.__response_match(resp, not_contains="in")
        
        resp = self.create_request(requests.text_bbbaaa)
        self.__response_match(resp, not_contains="bbb")
        self.__response_match(resp, contains="in")
        
        resp = self.create_request(requests.text_zzz)
        self.__response_match(resp, contains="unknown")
        
    def test_4_common(self):
        resp = self.create_request(requests.voice)
        self.__response_match(resp, contains="unknown")
        # bad request
        resp = self.create_request(requests.badrequest)
        self.__response_match(resp, status_code=400, xml=False)
        
        resp = self.app.post(self.posturl, data=requests.image, 
            content_type="text/xml")
        self.__response_match(resp, status_code=400, xml=False)
        # handler exception
        resp = self.create_request(requests.exception)
        self.__response_match(resp, xml=False)
        
    def __response_match(self, resp, status_code=200, xml=True, contains="",
        not_contains=""):
        data = resp.data.decode("utf8")
        self.assertTrue(resp.status_code==status_code, resp.status_code)
        if xml:
            self.assertTrue(resp.mimetype=="text/xml", resp.mimetype)
            self.assertTrue(re.match(self.pattern, data))
        else:
            self.assertTrue(resp.mimetype=="text/html", resp.mimetype)
        if contains:
            self.assertTrue(data.find(contains)>=0)
        if not_contains:
            self.assertFalse(data.find(not_contains)>=0)