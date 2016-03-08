#encoding:utf8

from functools import reduce
import re

def _combine_funcs(funcs):
    def __call(*args, **kwargs):
        return reduce(lambda func_a, func_b:\
            func_a(*args, **kwargs) and func_b(*args, **kwargs), funcs)
    return __call

# 所有
all = lambda m: True
# 事件
event = lambda m: m.msgtype=="event"
# 订阅
subscribe = _combine_funcs([event, lambda m: m.event=="subscribe"])
# 取消订阅
unsubscribe = _combine_funcs([event, lambda m: m.event=="unsubscribe"])
# 消息
message = lambda m: m.msgtype!="event"
# 文本消息
text = lambda m: m.msgtype=="text"
# 图片消息
image = lambda m: m.msgtype=="image"
# 声音消息
voice = lambda m: m.msgtype=="voice"
# 视频消息
video = lambda m: m.msgtype=="video"
# 小视频消息
shortvideo = lambda m: m.msgtype=="shortvideo"
# 包含
contains = lambda s, i=False: _combine_funcs([text,
	lambda m: m.content.lower().find(s.lower())>=0 if i else m.content.find(s)>=0])
# 开头
startswith =  lambda s, i=False: _combine_funcs([text, 
	lambda m: m.content.lower().find(s.lower())==0 if i else m.content.find(s)==0])
# 等于
equals = lambda s, i=False: _combine_funcs([text, 
	lambda m: m.content.lower()==s.lower() if i else m.content==s])
# 正则
regex = lambda p, fl=0, i=False: _combine_funcs([text, 
	lambda m: not not re.match(p, m.content, fl)])
# 在下列状况中
# def in_(list, accuracy=False, ignorecase=False):
#     def func(message):
#         for item in list:
#             if ignorecase:
#                 content = item.content.lower()
#                 item = item.lower()
                
#     return func