#encoding: utf8

from flask import Flask
from wechat import filters, WeChat, WeChatResponse

app = Flask(__name__)

wechat = WeChat(app)

@wechat.config_getter
def get_config(id):
    return dict(
        appid="123"
    ) if id=="tmp" else dict()

@wechat.message_handler("tmp", filters.subscribe)
def subscribe(message):
    return quick_response("欢迎关注")

@wechat.message_handler("tmp")
def all(message):
    return quick_response("听不懂呢")

@wechat.message_handler("tmp", filters.contains("妈个鸡"))
def subscribe(message):
    return quick_response("草泥马")

@wechat.message_handler("tmp", filters.contains("受不了了"))
def subscribe(message):
    return quick_response("小妖精 看我不操烂你的逼")

def quick_response(text):
    return WeChatResponse(msgtype="text", content=text)

@app.route("/")
def home():
    from flask import render_template
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)