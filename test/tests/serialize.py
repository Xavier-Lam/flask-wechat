#encoding:utf8

import re

from . import BaseTest
from ..data import data

from flask_wechat.messages import *

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
        pattern = r"^<xml>(?:\s*<([a-zA-Z0-9_]+)>.*?</\1>)+\s*</xml>$"
        for message, obj in self.messages.items():
            serialized = obj.serialize()
            self.assertTrue(re.match(pattern, serialized), serialized)
            # 验证该有的key是否都有了
            error_key = self.__serialized_items(obj, serialized)
            self.assertFalse(error_key, error_key)
            self.serialized[message] = serialized
        
    def test_3_deserialize(self):
        deserialized = dict()
        for message, string in self.serialized.items():
            deserialized[message] = WeChatMessageBase.deserialize(string)
        for message, obj in deserialized.items():
            for key, value in obj.items():
                self.assertTrue(self.messages[message][key]==value, key)
                
    def __serialized_items(self, message, serialized):
        str_pattern = r"<{name}><![CDATA[{value}]]></{name}>"
        num_pattern = r"<{name}>{value}</{name}>"
        for key, type in message.__fields__.items():
            if hasattr(message, key.lower()):
                value = getattr(message, key.lower())
                if type==str and not serialized.find(
                    str_pattern.format(name=key, value=value))>=0:
                    return key
                elif (type==int or type==float) and not serialized.find(
                    num_pattern.format(name=key, value=value))>=0:
                    return key
        return ""   