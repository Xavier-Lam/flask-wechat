#encoding: utf8

from flask import Flask
from wechat import filters, WeChat

app = Flask(__name__)
# app.config["DEBUG"] = True

wechat = WeChat()

@wechat.config_getter
def get_config(id):
    return dict(
        appid=app.config["appid"]
    ) if id==app.config["id"] else dict()

@wechat.handler("test", filters.event.subscribe)
def subscribe(message):
    return message.reply_text("welcome")

@wechat.handler("test")
def all(message):
    return message.reply_text("unknown")
    
@wechat.handler("test", filters.message.image)
def image(message):
    return message.reply_text("image")
    
@wechat.handler("test", filters.message.in_(["aaa", "ddd"]))
def in_(message):
    return message.reply_text("in")
    
@wechat.handler("test", filters.message.startswith("aaa"))
def aaa(message):
    return message.reply_text("bbb")
    
@wechat.handler("test", filters.message.text("exception"))
def exception(message):
    raise Exception()