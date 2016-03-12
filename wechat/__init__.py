#encoding:utf8

from collections import defaultdict
from functools import reduce, wraps
from xml.etree import ElementTree

from flask import Blueprint

from .filters import all as filter_all
from .filters import and_


#region patch
def _patch():
    def CDATA(text=None):
        element = ElementTree.Element("![CDATA[")
        element.text = text
        return element

    ElementTree.CDATA = CDATA

    ElementTree._original_serialize_xml = ElementTree._serialize_xml
    def _serialize_xml(write, elem, qnames, namespaces, *args, **kwargs):
        if elem.tag == "![CDATA[":
            write("\n<%s%s]]>\n" % (
                    elem.tag, elem.text))
            return
        return ElementTree._original_serialize_xml(
            write, elem, qnames, namespaces, *args, **kwargs)
    ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml

_patch()
#endregion


__all__ = ["WeChat", "wechat_blueprint", "WeChatClient", "WeChatHTTPClient"]


#region configs
_default_configs = dict(
    WECHAT_CALLBACK_PREFIX="/wechat/callbacks",
);

def _get_app_config(app, key):
    return app.config.get(key) or _default_configs[key]
#endregion


_callable = lambda func: hasattr(func, "__call__")


#region blueprint
class WeChatBlueprint(Blueprint):
    __core = None
    @property
    def core(self):
        if not isinstance(self.__core, WeChat):
            raise UnboundLocalError("you should init wechat module first!")
        return self.__core

    @core.setter
    def core(self, value):
        self.__core = value

wechat_blueprint = WeChatBlueprint("wechat", __name__)
#endregion


class WeChat(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)
        
    def init_app(self, app):
        self.app = app
        app.wechat = self
        wechat_blueprint.core = self
        
        app.register_blueprint(wechat_blueprint, 
            url_prefix=_get_app_config(app, "WECHAT_CALLBACK_PREFIX"))

    #region account configs
    def config_getter(self, func):
        """
        设置获取微信配置的装饰器
        传入配置id 获取app的配置
        """
        self.__get_account_config = func
        return func

    def accesstoken(self, func):
        """
        获取或设置微信token
        """
        self.__accesstoken = func
        return func
    #endregion

    #region module inner only
    __get_account_config = None
    def _get_config(self, identity):
        if not self.__get_account_config:
            raise Exception("no config_getters registered")
        return self.__get_account_config(identity)

    __accesstoken = None
    def _accesstoken_maintainer(self, identity, value=""):
        if not self.__accesstoken:
            raise Exception("no accesstoken maintainer registered")
        return self.__accesstoken(identity, value)
    #endregion
        
    #region handlers
    _handlers = defaultdict(list)
    def handler(self, identity="", filters=None):
        """
        注册消息处理器
        传入配置id 与filter 其中filter接收一个WeChatMessageBase类型传参
        """
        def decorator(func):
            nonlocal filters
            if not filters:
                filters = filter_all
            elif isinstance(filters, list):
                if len(list(filter(lambda f: not _callable(f), filters))):
                    raise TypeError("filters must be callable")
                # 合并过滤器
                filters = and_(filters)
            elif not _callable(filters):
                raise TypeError("filters must be callable")

            for tuple in self._handlers[identity]:
                if tuple[0]==filters:
                    del self._handlers[identity][tuple]
                    break

            if filters==filter_all:
                self._handlers[identity].append((filters, func))
            else:
                self._handlers[identity].insert(0, (filters, func))
            return func

        return decorator

    def handle_message(self, identity, message):
        """处理消息"""
        handler = self.__get_handler(identity, message)
        if not handler:
            return None
        try:
            return handler(message)
        except Exception as e:
            from .signals import response_error
            response_error.send(self, e)
            return None
        
    def __get_handler(self, identity, message):
        for filter, handler in self._handlers[identity]:
            if filter(message):
                return handler
        for filter, handler in self._handlers[""]:
            if filter(message):
                return handler
        return None
    #endregion

    #region interceptors
    _interceptors = dict()
    def __get_interceptor(self, name):
        return self._interceptors.get("name")

    def __set_interceptor(self, name, func):
        if not __callable(func):
            raise TypeError("interceptor must be callable")
        self._interceptors[name] = func

    def message_received(self, func):
        self.__set_interceptor("message_received", func)

    def message_error(self, func):
        self.__set_interceptor("message_error", func)

    # def intercept_response(self, func):
    #     """拦截原有回复"""
    #     self.__set_interceptor("intercept_response", func)

    def response_sent(self, func):
        self.__set_interceptor("response_sent", func)

    # def intercept(self, name):
    #     interceptor = self.__get_interceptor(name)
    #     if not interceptor:
    #         interceptor = lambda *args, **kwargs: 
    #     def do_intercept(*args, **kwargs):
    #         pass
    #endregion
        
from . import callback
from .client import WeChatClient
from .httpclient import WeChatHTTPClient