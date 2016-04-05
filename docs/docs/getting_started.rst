
.. _getting_started:

=========================
 入门
=========================

创建实例
=================

.. code-block:: python

    from flask.ext.wechat import WeChat
    
    wechat = WeChat(app)
    
你也可以延迟初始化app

.. code-block:: python

    from flask.ext.wechat import WeChat
    
    wechat = WeChat()
    
    ...
    
    wechat.init_app(app)

    
注册获取配置函数
=================

你需要注册一个获取微信配置用的函数。这个函数使用 ** wechat.account ** 进行装饰。
被装饰函数接收一个参数id，使用者通过id辨别不同的公众号。
函数以字典形式返回该公众号的appid, appsecret, token。如果该id未被用户使用，则返回空字典。

如果你只使用到微信订阅号自动回复功能，你在返回的字典中可以忽略appsecret与appid，
如果你需要使用 :ref:`WeChatApiClient` 调用微信的API，则你需要返回全部参数。
如果你在在公众平台官网的开发者中心处设置了消息加密，则你还需要返回aeskey，
但目前消息加解密的功能还尚未实现。

.. code-block:: python

    @wechat.account
    def get_config(id):
        return dict(
            appid="appid",
            appsecret="appsecret",
            token="token"
        ) if id=="demo" else dict()
        
模块默认的回调地址是/wechat/callbacks/<id>/ ，开发者需将这个地址填入微信后台的回调地址。
这个值的修改可在 :ref:`config` 中进行。
        
    
注册消息处理器
=================

你可以这样注册一个消息处理器（handler）：

.. code-block:: python

    @wechat.handler("demo", filters.event.subscribe)
    def subscribe(message):
        return message.reply_text("Thank you for subscribe!")

要处理来自微信的消息，你需要注册消息处理器。
注册消息处理器使用@wechat.handler 装饰器，
装饰器接收两个参数，第一个参数是使用者定义的公众号id，
第二个参数是用于判断请求是否符合要求的 :ref:`filter` ，
暨进入该处理器的条件。

一条消息只会进入一个处理器。

如果你要同时匹配多个过滤器，可以这样传入：

.. code-block:: python

    @wechat.handler("demo", 
        [filters.message.startswith("hello"), filters.message.contains("world")])

被装饰函数接收一个参数 :ref:`WeChatRequest` 对象，返回一个 :ref:`WeChatResponse` 对象。

WeChatRequest对象的属性包含微信公众平台开发者文档中该微信请求的所有有效字段。
所有属性为全部小写。WeChatResponse对象同理。

.. warning::

    除 filters.all 过滤器以外，越迟定义的过滤器拥有越高优先级！
    

过滤器
=================

模块自定义了一些过滤器方便用户使用。你可以通过

.. code-block:: python

    from flask.ext.wechat import filters
    
来使用他们。关于过滤器的详细说明，可以参考 :ref:`filter`章节。
    

拦截器
=================

*** 尚未实现 ***


信号
=================

你可以通过订阅信号的形式了解一些状态的变化，并处理一些逻辑。以下是一个简单的例子：

.. code-block:: python

    import logging
    from flask.ext.wechat import signals
    
    def callback(sender, identity, **kwargs):
        logging.info("{identity} sent response: {response}"\
            .format(identity=identity, response=kwargs["response"]))
    
    signals.response_sent.connect(callback, wechat)
    
信号的发送者为WeChat扩展实例，信号将至少接收一个identity参数，暨访问者自定义的公众号id。
在本例中，我们注册了回复已发送的信号。该信号发送于已接收到微信请求，并且成功回复以后。
不包括微信请求异常（Bad Request）回复的状况，但包含控制器抛出未经处理的异常的状况。

注意，使用信号需要安装blinker模块。

关于信号的详细说明，可以参考 :ref:`signal`章节。


请求微信API
=================

微信提供了很多Restful API供开发者调用。通过WeChatApiClient，
开发者可以方便地调用微信的API。

要使用WeChatApiClient，你需要在@wechat.account装饰的函数返回的字典中包含
appid与appsecret项。

并且，你需要注册一个维持公众号accesstoken的函数。

.. code-block:: python

    @wechat.accesstoken
    def accesstoken(identity, value="", expires_in=7200):
        return "accesstoken"
        
这个函数使用@wechat.accesstoken 装饰，
被装饰的函数包含3个参数，用户定义的公众号id，新的accesstoken值，accesstoken过期时间。

当WeChatApiClient需要获取accesstoken时，会传入用户定义的公众号id，
你需要返回已知的该公众号accesstoken，如果未知，则返回空。

如果WeChatApiClient更新了accesstoken，会传入用户定义的公众号id，
新的accesstoken值，新accesstoken的在多久以后过期。

.. note::

    建议用户在数据库或cache中维持这个accesstoken，避免每次请求时都对公众号重新获取授权。
    

WeChatApiClient 构造函数接受一个参数，用户自定义的公众号id。

.. code-block:: python

    from flask.ext.wechat import WeChatApiClient
    
    client = WeChatApiClient("test")
    
调用接口时，用户需要传入接口的url以及其他的一些附加参数，
这些附加参数与python的requests模块一致。可以参见requests模块文档。

.. note:: 

    接口url默认为 https://api.weixin.qq.com/ ，前缀/cgi_bin 。
    如果你需要修改url地址，可以通过修改client的 __baseaddr__ 属性和 __prefix__ 属性来实现。

WeChatApiClient包含三个请求方法 get, get_raw, post。

.. code-block:: python

    resp, code = client.get("/get_current_selfmenu_info")
    resp, code = client.post("/menu/create", json=dict(button=[{
        "type":"view",
        "name":"搜索",
        "url":"http://www.soso.com/"
    }]))

get与post方法返回两个值，第一个值为解析为字典后的返回对象，第二个值为返回中的errcode。
如果code=0 可以认为请求成功。如果code=-2 则说明请求返回的数据异常，无法正常解析（如不是json）。

.. code-block:: python

    resp = client.get_raw("/get_current_selfmenu_info")
    
get_raw 方法直接返回requests.Response 对象。

.. note::
    
    WeChatApiClient 会在用户请求的querystring上自动加上accesstoken。
    当accesstoken过期或是不存在时，WeChatApiClient会尝试更新一次accesstoken。