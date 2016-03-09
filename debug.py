#encoding: utf8

from flask import Flask
from flask.ext.script import Manager, Shell
from wechat import filters, WeChat

app = Flask(__name__)
app.debug = True

wechat = WeChat(app)

@wechat.config_getter
def get_config(id):
    return dict(
        appid="wxc908fb07bc49c284",
        appsecret="121ed8930e99a520e3ff7db796f17031"
    )

@wechat.accesstoken
def accesstoken(id, value):
    return ""

@app.route("/")
def home():
    from wechat import WeChatClient
    client=WeChatClient(1)
    raise client
    return render_template("index.html")

manager = Manager(app)

def shell(config):
    """
    run flask shell
    """
    from wechat import WeChatHTTPClient
    shell = Shell(make_context=lambda: dict(app=app, client=WeChatHTTPClient(1)))
    shell.run(True, False)
    
if __name__ == "__main__":
    manager.run()