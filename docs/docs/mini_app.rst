
=========================
 一个最小应用
=========================

该应用首先初始化了Flask-WeChat扩展，随后注册id为demo的公众号，
当接收到id为demo的公众号的回调时，返回该公众号的配置。
在应用中，开发者通过扩展内预定义的过滤器（filters），
注册了订阅事件、所有事件、接收到以hello开头的文本事件三种事件的处理器。
当应用收到用户发送的微信消息时，将找到对应的处理事件，并根据处理事件的返回，
进行相应回复。

.. code-block:: python

    from flask import Flask
    from flask.ext.wechat import filters, WeChat

    app = Flask(__name__)

    wechat = WeChat(app)

    @wechat.account
    def get_config(id):
        return dict(
            appid="appid",
            appsecret="appsecret",
            token="token"
        ) if id=="demo" else dict()

    @wechat.handler("demo", filters.event.subscribe)
    def subscribe(message):
        return message.reply_text("Thank you for subscribe!")

    @wechat.handler("demo")
    def all(message):
        return message.reply_text("I'm confused...")
        
    @wechat.handler("demo", filters.message.startswith("hello"))
    def hello(message):
        return message.reply_text("world")

    if __name__ == "__main__":
        app.run()