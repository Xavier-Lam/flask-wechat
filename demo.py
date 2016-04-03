#encoding: utf8

from flask import Flask
from wechat import filters, WeChat

app = Flask(__name__)

wechat = WeChat(app)

@wechat.config_getter
def get_config(id):
    return dict(
        appid="123"
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

@app.route("/")
def home():
    from flask import render_template
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)