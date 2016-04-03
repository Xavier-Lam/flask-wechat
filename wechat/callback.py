#encoding:utf8

from flask import abort, current_app, request, Response
from . import signals
from . import wechat_blueprint as wechat
from .messages import WeChatMessageBase, WeChatResponse
from .services.accesstoken import get_token

@wechat.route("/<identify>/", methods=["GET"])
def verify(identify):
    _send_signal("verify_received", appid, request)
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    echostr = request.args.get("echostr")

    if not (signature and timestamp and nonce and echostr):
        _send_signal("verify_failed", 400)
        abort(400)
    if not _verify_request(signature, timestamp, nonce):
        _send_signal("verify_failed", 401)
        abort(401)
    send("verify_successed", appid)
    return echostr

@wechat.route("/<identify>/", methods=["POST"])
def callback(identify):
    response = None
    message = WeChatMessageBase.deserialize(request.data)
    if not message:
        _send_signal("request_badrequest", request.data)
        abort(400) # 值得商榷
    _send_signal("request_received", message)
        
    try:
        # interceptor = wechat.core.get_interceptor("message_received")
        # if interceptor:
        #     message = interceptor(message)
        # if not isinstance(message, WeChatMessageBase):
        #     return ""
        response = wechat.core.handle_message(identify, message)
    except Exception as e:
        _send_signal("request_handle_error", e)
        if wechat.core.debug: raise
        return ""
        # interceptor = wechat.core.get_interceptor("message_error")
        # if interceptor:
        #     response = interceptor(message)

    if isinstance(response, WeChatResponse):
        rv = _send_repsonse(response)
        _send_signal("response_sent", response)
        return rv
    else:
        return ""

def _verify_request(signature, timestamp, nonce):
     account = current_app.weixin.get_account(appid)
     if not account:
        _send_signal("verify_failed", 404)
        abort(404)
     arr = [account["token"], timestamp, nonce]
     arr.sort()
     string = "".join(arr)
     
     from hashlib import sha1
     server_sign = sha1(string.encode()).hexdigest()
     return server_sign == signature

def _send_signal(signal, *args, **kwargs):
    if hasattr(signals, signal):
        send = getattr(signals, signal).send
        send(wechat.core, *args, **kwargs)
    elif wechat.core.debug: raise KeyError(signal)

def _send_repsonse(response):
    return Response(response.serialize(), mimetype="text/xml")