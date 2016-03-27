#encoding:utf8

from functools import reduce
import re

__all__ = ["all", "and_", "event", "message", "or_"]

_typeof = lambda t: lambda m: m.msgtype==t

def _match(message, contains, accuracy=True, ignorecase=False):
    """帮助匹配文本的函数"""
    if ignorecase:
        message = message.lower()
        contains = contains.lower()
    if accuracy:
        return 0 if message==contains else -1
    else:
        return message.find(contains)

class Filter(object):
    def __call__(self, message):
        raise NotImplementedError()

class Event(Filter):
    def __call__(self, message, type=None):
        rv = message.msgtype == "event"
        if rv and type:
            return message.event == type
        return rv

    # 订阅
    subscribe = lambda self, m: self(m, "subscribe")
    # 取消订阅
    unsubscribe = lambda self, m: self(m, "unsubscribe")
    # 点击
    def click(self, key=None):
        def decorated_func(message):
            rv = self(message, "CLICK")
            if rv and key:
                return message.eventkey==key
            return rv
        return decorated_func
    # 点击跳转
    def view(self, url=None, accuracy=False, ignorecase=False):
        def decorated_func(message):
            rv = self(message, "VIEW")
            if rv and url:
                return _match(message.eventkey, url, accuracy, ignorecase)>=0
            return rv
        return decorated_func

class Message(Filter):
    def __call__(self, message, text=None, ignorecase=False):
        rv = message.msgtype != "event"
        if rv and text and self.typeof(message, "text"):
            return _match(message.content, text, True, ignorecase)
        return rv

    # 是某种类型的消息
    typeof = lambda self, t: lambda m: m.msgtype==t
    # 文字消息
    text = staticmethod(_typeof("text"))
    # text = lambda self, m: self.typeof("text")(m)
    # 图片消息
    image = staticmethod(_typeof("image"))
    # image = lambda self, m: self.typeof("image")(m)
    # 声音消息
    voice = staticmethod(_typeof("voice"))
    # voice = lambda self, m: self.typeof("voice")(m)
    # 视频消息
    video = staticmethod(_typeof("video"))
    # video = lambda self, m: self.typeof("video")(m)
    # 小视频消息
    shortvideo = staticmethod(_typeof("shortvideo"))
    # shortvideo = lambda self, m: self.typeof("shortvideo")

    contains = lambda self, s, i=False:\
        lambda m: self.text() and _match(m.content, s, False, i)>=0
    # 开头
    startswith = lambda self, s, i=False:\
        lambda m: self.text() and _match(m.content, s, False, i)==0
    # 正则
    regex = lambda self, p, fl=0:\
        lambda m: self.text() and not not re.match(p, m.content, fl)
        
    # 文本在下列某种状况中
    def in_(self, list, comparer=None):
        if not comparer:
            comparer = self.contains
        def func(message):
            for item in list:
                if comparer(item)(message):
                    return True
            return False
        return func

    # 在下列正则中
    def regex_in(self, patterns):
        def func(message):
            for pattern in patterns:
                if re.match(pattern, message):
                    return True
            return False
        return and_(text, func)

# 所有
all = lambda m: True
# 满足全部
def and_(*funcs):
    def __call(*args, **kwargs):
        return reduce(lambda func_a, func_b: (func_a if type(func_a) == bool else \
            func_a(*args, **kwargs)) and func_b(*args, **kwargs), funcs)
    return __call
# 满足其一
def or_(*funcs):
    def __call(*args, **kwargs):
        return reduce(lambda func_a, func_b: (func_a if type(func_a) == bool else \
            func_a(*args, **kwargs)) or func_b(*args, **kwargs), funcs)
    return __call

event = Event()
message = Message()

# # 在下列状况中
# def in_(list, accuracy=False, ignorecase=False):
#     def func(message):
#         for item in list:
#             content = message.content
#             if ignorecase:
#                 content = content.lower()
#                 item = item.lower()
#             if content.find(item)>=0:
#                 return True
#         return False
#     return _combine_funcs(text, func)