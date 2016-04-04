#encoding: utf8

from collections import defaultdict
from contextlib import contextmanager
import os

from . import BaseTest
from ..context import signal_context

from flask import Flask
from flask_wechat import signals, WeChat, WeChatApiClient

app = Flask(__name__)
wechat = WeChat()

@contextmanager
def context():
    try:
        accesstoken = defaultdict(str)
        def decorated_func(identity, value=None):
            if value:
                accesstoken[identity] = value
            return accesstoken[identity]
        wechat.accesstoken(decorated_func)
        yield decorated_func, accesstoken
    finally:
        wechat.accesstoken(None)

class ApiClientTestCases(BaseTest):
    identity = "test"
    appid = "wxc908fb07bc49c284"
    appsecret = "121ed8930e99a520e3ff7db796f17031"

    def setUp(self):
        super(ApiClientTestCases, self).setUp()
        assert self.appid
        assert self.appsecret
        wechat.account(lambda id: dict(
            appid=self.appid, 
            appsecret=self.appsecret) if id==self.identity else {})
        wechat.init_app(app)

    def test_1_grant(self):
        with context() as (maintainer, collection):
            # 正常授权
            client = WeChatApiClient(self.identity)
            accesstoken = client.grant()
            self.assertTrue(accesstoken)
            self.assertTrue(accesstoken == collection[self.identity])
            self.assertTrue(accesstoken == maintainer(self.identity))
            
            # 过期后重新授权
            with signal_context(signals.wechat_granted, wechat) as records:
                # 继续请求无需重新获取授权
                client = WeChatApiClient(self.identity)
                resp, code = client.get("/get_current_selfmenu_info")
                self.assertFalse(code)
                self.assertTrue("is_menu_open" in resp)
                self.assertTrue(accesstoken==client.accesstoken)
                self.assertFalse(len(records))
                
                # 授权过期重新请求授权并发送信号并获得正确结果
                expired = "expired"
                collection[self.identity] = expired
                self.assertTrue(maintainer(self.identity)==expired)
                client = WeChatApiClient(self.identity)
                resp, code = client.get("/get_current_selfmenu_info")
                self.assertFalse(code)
                self.assertTrue("is_menu_open" in resp)
                self.assertFalse(accesstoken==client.accesstoken)
                self.assertFalse(maintainer(self.identity)==expired)
                self.assertTrue(len(records)==1)
        
    def test_2_requests(self):
        with context() as (maintainer, collection):
            self.assertFalse(maintainer(self.identity))
            # post 请求
            client = WeChatApiClient(self.identity)
            resp, code = client.post("/menu/create", json=dict(button=[{
               "type":"view",
               "name":"搜索",
               "url":"http://www.soso.com/"
            }]))
            self.assertFalse(code)
            
            # 文件上传
            client = WeChatApiClient(self.identity)
            filename = "./test/image.png"
            filesize = str(os.path.getsize(filename))
            file = ("test.png", open(filename, "rb"), "image/png")
            resp, code = client.post("/media/upload", params=dict(type="image"), 
                files=dict(files=file))
            media_id = resp["media_id"]
            self.assertTrue(media_id)
            self.assertFalse(code)
            
            # 获取刚上传的文件
            client = WeChatApiClient(self.identity)
            resp = client.get_raw("/media/get", params=dict(media_id=media_id))
            self.assertTrue(resp.status_code==200)
            self.assertTrue(resp.headers["Content-Type"].startswith("image"))
            self.assertTrue(resp.headers["Content-Length"]==filesize)