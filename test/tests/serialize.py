#encoding:utf8

from . import BaseTest
from ..data import data

from wechat.messages import *

class SerializeTestCases(BaseTest):
    messages = dict()
    serialized = dict()

    def test_1_init(self):
        # messages["event_subscribe"] = WeChatMessageEvent(**self.data["event_subscribe"])
        # messages["event_barcode"] = WeChatMessageEvent(**self.data["event_barcode"])
        # messages["event_click"] = WeChatMessageEvent(**self.data["event_click"])
        # messages["event_view"] = WeChatMessageEvent(**self.data["event_view"])
        for message_type, message in data.items():
            if message_type.startswith("event"):
                self.messages[message_type] = WeChatEvent(**message)
            elif message_type.startswith("message"):
                self.messages[message_type] = WeChatMessage(**message)
        for message, obj in self.messages.items():
            for key, value in data[message].items():
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