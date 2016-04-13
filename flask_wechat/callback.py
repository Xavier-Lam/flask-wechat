#encoding:utf8

import time
from flask import abort, current_app, request, Response
from . import signals
from . import wechat_blueprint as wechat
from .messages import WeChatMessageBase, WeChatResponse

@wechat.route("/<identity>/", methods=["GET", "POST"])
def callback(identity):
    _send_signal("request_received", identity, 
        request=request)
    # 验证请求
    signature = request.args.get("signature")
    try:
        timestamp = int(request.args.get("timestamp"))
    except:
        _send_signal("request_badrequest", identity, request=request, 
            message="incorrect timestamp")
        abort(400)
    nonce = request.args.get("nonce")

    if not (signature and timestamp and nonce):
        _send_signal("request_badrequest", identity, request=request, 
            message="incorrect args")
        abort(400)
    if abs(time.time() - timestamp) >= 15*60:
        _send_signal("request_badrequest", identity, request=request, 
            message="incorrect time")
        abort(400)
    if not _verify_request(identity, signature, timestamp, nonce):
        _send_signal("request_badrequest", identity, request=request, 
            message="incorrect signature")
        abort(401)
    if request.method=="GET":
        echostr = request.args.get("echostr")
        if not echostr:
            _send_signal("request_badrequest", identity, request=request, 
            message="incorrect args")
            abort(400)
        _send_signal("response_sent", identity, request=request, response=echostr)
        return echostr
        
    # 反序列化body
    response = None
    message = WeChatMessageBase.deserialize(request.data)
    if not message:
        _send_signal("request_badrequest", identity, request=request, 
            message="incorrect content")
        abort(400) # 值得商榷
    _send_signal("request_deserialized", identity, message=message)
        
    try:
        # interceptor = wechat.core.get_interceptor("message_received")
        # if interceptor:
        #     message = interceptor(message)
        # if not isinstance(message, WeChatMessageBase):
        #     return ""
        response = wechat.core.handle_message(identity, message)
    except Exception as e:
        _send_signal("request_handle_error", identity, request=request,
            exception=e)
        _send_signal("response_sent", identity, request=request, response="")
        if wechat.core.debug: raise
        return ""
        # interceptor = wechat.core.get_interceptor("message_error")
        # if interceptor:
        #     response = interceptor(message)

    if isinstance(response, WeChatResponse):
        rv = _send_repsonse(response)
        _send_signal("response_sent", identity, request=request, response=response)
    else:
        rv = "success"
        _send_signal("response_sent", identity, request=request, response="success")
    return rv

def _verify_request(identity, signature, timestamp, nonce):
     account = wechat.core._get_config(identity)
     if not account:
        _send_signal("request_badrequest", identity, message="identity not found")
        abort(404)
     arr = [account["token"], str(timestamp), nonce]
     arr.sort()
     string = "".join(arr)
     
     from hashlib import sha1
     server_sign = sha1(string.encode()).hexdigest()
     return server_sign == signature

def _send_signal(signal, identity, **kwargs):
    if hasattr(signals, signal):
        getattr(signals, signal).send(wechat.core, identity=identity, **kwargs)
    elif wechat.core.debug: raise KeyError(signal)

def _send_repsonse(response):
    return Response(response.serialize(), mimetype="text/xml")