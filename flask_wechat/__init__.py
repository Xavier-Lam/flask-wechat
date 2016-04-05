#encoding:utf8

from collections import defaultdict
from functools import reduce, wraps
from xml.etree import ElementTree

from flask import Blueprint

from .filters import all as filter_all
from .filters import and_

__all__ = ["WeChat", "wechat_blueprint", "WeChatApiClient"]


#region configs
_default_configs = dict(
    WECHAT_CALLBACK_PREFIX="/wechat/callbacks",
    WECHAT_DEBUG=False
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
        self.callback_prefix = _get_app_config(app, "WECHAT_CALLBACK_PREFIX")
        self.debug = _get_app_config(app, "WECHAT_DEBUG")
        app.wechat = self
        wechat_blueprint.core = self
        
        app.register_blueprint(wechat_blueprint, 
            url_prefix=self.callback_prefix)

    #region account configs
    def account(self, func):
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
            raise RuntimeError("no account function registered")
        return self.__get_account_config(identity)

    __accesstoken = None
    def _accesstoken_maintainer(self, identity, value="", expires_in=7200):
        if not self.__accesstoken:
            raise RuntimeError("no accesstoken maintainer registered")
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
            filters_ = filters
            if not filters_:
                filters_ = filter_all
            elif isinstance(filters_, list):
                if len(list(filter(lambda f: not _callable(f), filters_))):
                    raise TypeError("filters must be callable")
                # 合并过滤器
                filters_ = and_(filters_)
            elif not _callable(filters_):
                raise TypeError("filters must be callable")

            # 覆盖原有handler
            for tuple in self._handlers[identity]:
                if tuple[0]==filters_:
                    del self._handlers[identity][tuple]
                    break

            if filters_==filter_all:
                self._handlers[identity].append((filters_, func))
            else:
                self._handlers[identity].insert(0, (filters_, func))
            return func

        return decorator

    def handle_message(self, identity, message):
        """处理消息"""
        handler = self.__get_handler(identity, message)
        if not handler:
            return None
        # try:
        return handler(message)
        # except Exception as e:
        #     from .signals import response_error
        #     response_error.send(self, e)
        #     if self.debug: raise
        #     return None
        
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
from .apiclient import WeChatApiClient