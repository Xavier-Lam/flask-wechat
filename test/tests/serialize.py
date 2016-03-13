#encoding:utf8

from . import BaseTest

from wechat.messages import *
 
def theirsmessage(**kwargs):
    return dict(
        fromusername="they",
        tousername="me",
        createtime=1457600000,
        **kwargs
    )

def minemessage(**kwargs):
    return dict(
        fromusername="me",
        tousername="they",
        createtime=1457600000,
        **kwargs
    )

class SerializeTestCases(BaseTest):
    data = dict(
        event_subscribe=theirsmessage(
            msgtype="event",
            event="subscribe"
        ),
        event_barcode=theirsmessage(
            msgtype="event",
            event="SCAN",
            eventkey="scene_value",
            ticket="ticket"
        ),
        event_view=theirsmessage(
            msgtype="event",
            event="VIEW",
            eventkey="www.xavier-lam.com",
        ),
        event_click=theirsmessage(
            msgtype="event",
            event="CLICK",
            eventkey="EVENTKEY",
        ),
        message_text=theirsmessage(
            msgtype="type",
            content="中文",
            msgid=12345,
        ),
        message_pic=theirsmessage(
            msgtype="image",
            picurl="http://wechat.xavier-lam.com/example.jpg",
            msgid=12345,
            mediaid="123456",
        ),
        message_voice=theirsmessage(
            msgtype="voice",
            format="arm",
            msgid=12345,
            mediaid="123456",
        ),
        message_voice_with_rec=theirsmessage(
            msgtype="voice",
            format="arm",
            recognition="我嘞个去",
            msgid=12345,
            mediaid="123456",
        ),
        message_video=theirsmessage(
            msgtype="voice",
            thumbmediaid="asdfds",
            msgid=12345,
            mediaid="sadsasdf",
        ),
        message_shortvideo=theirsmessage(
            msgtype="shortvoice",
            thumbmediaid="asdfds",
            msgid=12345,
            mediaid="sadsasdf",
        ),
        message_location=theirsmessage(
            msgtype="location",
            location_x=123.12,
            location_y=321.32,
            scale=12,
            label="851大楼",
            msgid=24435345
        ),
        message_url=theirsmessage(
            msgtype="link",
            title="标题",
            description="概述",
            url="http://www.xavier-lam.com/",
            msgid=1232131
        ),
    )

    messages = dict()
    serialized = dict()

    def test_1_init(self):
        # messages["event_subscribe"] = WeChatMessageEvent(**self.data["event_subscribe"])
        # messages["event_barcode"] = WeChatMessageEvent(**self.data["event_barcode"])
        # messages["event_click"] = WeChatMessageEvent(**self.data["event_click"])
        # messages["event_view"] = WeChatMessageEvent(**self.data["event_view"])
        for message_type, message in self.data.items():
            if message_type.startswith("event"):
                self.messages[message_type] = WeChatEvent(**message)
            elif message_type.startswith("message"):
                self.messages[message_type] = WeChatMessage(**message)
        for message, obj in self.messages.items():
            for key, value in self.data[message].items():
                self.assertTrue(obj[key]==value, key)

    def test_2_serialize(self):
        for message, obj in self.messages.items():
            self.serialized[message] = obj.serialize()
        # 应验证格式
        pass
        
    def test_3_deserialize(self):
        deserialized = dict()
        for message, string in self.serialized.items():
            deserialized[message] = WeChatMessageBase.deserialize(string)
        for message, obj in deserialized.items():
            for key, value in obj.items():
                self.assertTrue(self.messages[message][key]==value, key)