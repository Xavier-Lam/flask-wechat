#encoding:utf8

from flask.signals import Namespace

__all__ = ["verify_failed", "verify_received", "verify_successed", 
    "request_badrequest", "request_handle_error", "request_received", 
    "response_error", "response_sent", "wechat_servererror", "wechat_error"]

signals = Namespace()

verify_received = signals.signal("verify_received")
verify_successed = signals.signal("verify_successed")
verify_failed = signals.signal("verify_failed")

request_received = signals.signal("request_received")
request_badrequest = signals.signal("request_badrequest")
request_handle_error = signals.signal("request_handle_error")
response_error = signals.signal("response_error")
response_sent = signals.signal("response_sent")

wechat_servererror = signals.signal("wechat_servererror")
wechat_error = signals.signal("wechat_error")