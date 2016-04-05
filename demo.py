#encoding: utf8

from flask import Flask
from flask_wechat import filters, signals, WeChat

app = Flask(__name__)

wechat = WeChat(app)

@wechat.account
def get_config(id):
    return dict(
        appid="123",
        token="654212"
    ) if id=="tmp" else dict()

@wechat.handler("tmp", filters.event.subscribe)
def subscribe(message):
    return message.reply_text("欢迎关注")

@wechat.handler("tmp")
def all(message):
    return message.reply_text("听不懂呢")

@wechat.handler("tmp", filters.message.contains("妈个鸡"))
def subscribe(message):
    return message.reply_text("草泥马")

@wechat.handler("tmp", filters.message.contains("受不了了"))
def subscribe(message):
    return message.reply_text("小妖精 看我不操烂你的逼")
    
@wechat.handler("tmp", filters.message.image)
def image(message):
    return message.reply_text("不要发图片给我了")
    
@wechat.handler("tmp", filters.message.contains("黄图"))
def reply_image(message):
    return message.reply_media("image", "0oFRnORCwofewx9NkTnuChjoraRtsiCBtR6DTtHVHcbjOeYeNy5mi0EJ7cFRHiqZ")
    
@wechat.handler("tmp", filters.message.location(119.3, 26.08, 2))
def reply_location(message):
    longitude = message.location_x 
    latitude = message.location_y
    return message.reply_text("你好像在福州，你的坐标是：" + longitude + " " + latitude)
    
@wechat.handler("tmp", filters.message.contains("图文"))
def articles(message):
    return message.reply_article([{
        "title": "这是第一条图文",
        "description": "具体描述",
        "picurl": "http://mp.weixin.qq.com/wiki/static/assets/dc5de672083b2ec495408b00b96c9aab.png",
        "url": "http://mp.weixin.qq.com/"
    }, {
        "title": "这是第二条图文",
        "description": "具体描述",
        "picurl": "http://mp.weixin.qq.com/wiki/static/assets/dc5de672083b2ec495408b00b96c9aab.png",
        "url": "http://mp.weixin.qq.com/"
    }])

@app.route("/")
def home():
    from flask import render_template
    return render_template("index.html")
    
def callback(sender, identity, response):
    print("")
    print(response)
    
def request_callback(sender, identity, message, **kwargs):
    from flask_wechat.messages import WeChatMessage
    if isinstance(message, WeChatMessage) and message.msgtype == "location":
        print("")
        print(message)
    
signals.response_sent.connect(callback, wechat)
signals.request_deserialized.connect(callback, wechat)

if __name__ == "__main__":
    app.run(debug=True)