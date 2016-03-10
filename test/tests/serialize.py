#encoding:utf8

from flask.ext.wechat.messages import *

from . import BaseTest

__all__ = ["SerializeTestCases"]

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
        )
    )

    messages = dict()

    def test_1_init(self):
        messages["event_subscribe"] = WeChatMessageEvent(**self.data["event_subscribe"])
        messages["event_barcode"] = WeChatMessageEvent(**self.data["event_barcode"])
        messages["event_click"] = WeChatMessageEvent(**self.data["event_click"])
        messages["event_view"] = WeChatMessageEvent(**self.data["event_view"])
        for message, obj in messages:
            for key, value in self.data[message]:
                self.assertTrue(getattr(obj, key)==value)

    def test_2_deserialize(self):
        pass

    def test_3_serialize(self):
        pass