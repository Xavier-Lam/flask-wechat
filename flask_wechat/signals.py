#encoding:utf8

from flask.signals import Namespace

__all__ = ["request_received", "request_deserialized", "request_badrequest", 
    "request_deserialize_error", "request_handle_error", "response_error", 
    "response_sent", "wechat_granted", "wechat_servererror", "wechat_error"]

signals = Namespace()

request_received = signals.signal("request_received")
request_deserialized = signals.signal("request_deserialized")
request_badrequest = signals.signal("request_badrequest")
# request_deserialize_error = signals.signal("request_deserialize_error")
request_handle_error = signals.signal("request_handle_error")

# response_error = signals.signal("response_error")
response_sent = signals.signal("response_sent")

wechat_granted = signals.signal("wechat_granted")
wechat_servererror = signals.signal("wechat_servererror")
wechat_error = signals.signal("wechat_error")