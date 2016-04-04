#encoding:utf8

import re

from . import BaseTest
from ..data import data, mine

from flask_wechat.messages import *
from flask_wechat.messages.subelement import WeChatResponseSubElement, WeChatResponseSubList

class SerializeTestCases(BaseTest):
    messages = dict()
    mine = dict()
    serialized = dict()

    def test_1_init(self):
        for message_type, message in data.items():
            if message_type.startswith("event"):
                self.messages[message_type] = WeChatEvent(**message)
            elif message_type.startswith("message"):
                self.messages[message_type] = WeChatMessage(**message)
        for message, obj in self.messages.items():
            for key, value in data[message].items():
                self.assertTrue(obj[key]==value, key)
        # 我发出的消息
        for message_type, message in mine.items():
            self.mine[message_type] = WeChatResponse(**message)
        for message, obj in self.mine.items():
            for key, value in mine[message].items():
                self.assertTrue(obj[key]==value, obj[key])
                
    def test_2_serialize(self):
        pattern = r"^<xml>(?:\s*<([a-zA-Z0-9_]+)>.*?</\1>)+\s*</xml>$"
        for message, obj in self.messages.items():
            serialized = obj.serialize()
            self.assertTrue(re.match(pattern, serialized), serialized)
            # 验证该有的key是否都有了
            error_key = self.__serialized_items(obj, serialized)
            self.assertFalse(error_key, error_key)
            self.serialized[message] = serialized
        # 我发出的消息
        for message, obj in self.mine.items():
            serialized = obj.serialize()
            self.assertTrue(re.match(pattern, serialized), serialized)
            # 验证该有的key是否都有了
            error_key = self.__serialized_items(obj, serialized)
            self.assertFalse(error_key, error_key)
        
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
        subelement_content = r"<{name}>(.*?)</{name}>"
        for key, type in message.__fields__.items():
            if hasattr(message, key.lower()):
                value = getattr(message, key.lower())
                if type==str and not serialized.find(
                    str_pattern.format(name=key, value=value))>=0:
                    return key
                elif (type==int or type==float) and not serialized.find(
                    num_pattern.format(name=key, value=value))>=0:
                    return key
                elif issubclass(type, WeChatResponseSubElement):
                    pattern = subelement_content.format(name=key)
                    match = re.search(pattern, serialized)
                    self.assertTrue(match)
                    group = match.group(1)
                    self.assertFalse(self.__serialized_items(value, group))
        return ""   