#encoding:utf8

import re, time
from hashlib import sha1

from . import BaseTest
from ..app import app, wechat

from wechat.messages import WeChatMessageBase    

class ResponseTestCases(BaseTest):
    identify = "test"
    token = "token"
    pattern = r"^<xml>(?:\s*<([a-zA-Z0-9_]+)>.*?</\1>)+\s*</xml>$"
        
    def setUp(self):
        super(ResponseTestCases, self).setUp()
        app.config["id"] = self.identify
        app.config["token"] = self.token
        # app.config["WECHAT_DEBUG"] = True
        # app.config["DEBUG"] = True
        self.app = app.test_client()
        wechat.init_app(app)
        self.posturl = wechat.callback_prefix +  "/" + self.identify + "/"
        
    def test_1_verify(self):
        echostr = "aaaaaa"
        url = self.posturl + self.__query_str + "&echostr=" + echostr
        resp = self.app.get(url)
        self.assertTrue(resp.data.decode("utf8")==echostr)
        self.__response_match(resp, xml=False)
        
    def test_2_request(self):
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[FromUser]]></FromUserName>
<CreateTime>123456789</CreateTime>
<MsgType><![CDATA[event]]></MsgType>
<Event><![CDATA[subscribe]]></Event>
</xml>""", content_type="text/xml")
        self.__response_match(resp, contains="welcome")
        # 图片
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName>
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[image]]></MsgType>
 <PicUrl><![CDATA[this is a url]]></PicUrl>
 <MediaId><![CDATA[media_id]]></MediaId>
 <MsgId>1234567890123456</MsgId>
 </xml>""", content_type="text/xml")
        self.__response_match(resp, contains="image")
        
    def test_3_text(self):
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName> 
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[ddd]]></Content>
 <MsgId>1234567890123456</MsgId>
 </xml>""")
        self.__response_match(resp, contains="in")
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName> 
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[aaab]]></Content>
 <MsgId>1234567890123456</MsgId>
 </xml>""")
        self.__response_match(resp, contains="bbb")
        self.__response_match(resp, not_contains="in")
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName> 
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[bbbaaa]]></Content>
 <MsgId>1234567890123456</MsgId>
 </xml>""")
        self.__response_match(resp, not_contains="bbb")
        self.__response_match(resp, contains="in")
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName> 
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[zzz]]></Content>
 <MsgId>1234567890123456</MsgId>
 </xml>""")
        self.__response_match(resp, contains="unknown")
        
    def test_4_common(self):
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>1357290913</CreateTime>
<MsgType><![CDATA[voice]]></MsgType>
<MediaId><![CDATA[media_id]]></MediaId>
<Format><![CDATA[Format]]></Format>
<MsgId>1234567890123456</MsgId>
</xml>""", content_type="text/xml")
        self.__response_match(resp, contains="unknown")
        # bad request
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>1357290913</CreateTime>""", content_type="text/xml")
        self.__response_match(resp, status_code=400, xml=False)
        resp = self.app.post(self.posturl, data="""<xml>
<ToUserName><![CDATA[toUser]]></ToUserName>
<FromUserName><![CDATA[fromUser]]></FromUserName>
<CreateTime>1357290913</CreateTime>
<MsgType><![CDATA[voice]]></MsgType>
<MediaId><![CDATA[media_id]]></MediaId>
<Format><![CDATA[Format]]></Format>
<MsgId>1234567890123456</MsgId>
</xml>""", content_type="text/xml")
        self.__response_match(resp, status_code=400, xml=False)
        # handler exception
        resp = self.app.post(self.posturl + self.__query_str, data="""<xml>
 <ToUserName><![CDATA[toUser]]></ToUserName>
 <FromUserName><![CDATA[fromUser]]></FromUserName> 
 <CreateTime>1348831860</CreateTime>
 <MsgType><![CDATA[text]]></MsgType>
 <Content><![CDATA[exception]]></Content>
 <MsgId>1234567890123456</MsgId>
 </xml>""", content_type="text/xml")
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
            
    @property
    def __query_str(self):
        nonce = "12345678"
        timestamp = str(int(time.time()))
        token = self.token
        arr = [token, timestamp, nonce]
        arr.sort()
        string = "".join(arr)
        sign = sha1(string.encode()).hexdigest()
        return "?nonce={nonce}&timestamp={timestamp}&signature={sign}".format(
            nonce = nonce,
            timestamp = timestamp,
            sign=sign
        )