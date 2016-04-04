
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

你需要注册一个获取微信配置用的函数。这个函数使用 ** wechat.config_getter ** 进行装饰。
被装饰函数接收一个参数id，使用者通过id辨别不同的公众号。
函数以字典形式返回该公众号的appid, appsecret, token。如果该id未被用户使用，则返回空字典。

如果你只使用到微信订阅号自动回复功能，你在返回的字典中可以忽略appsecret与appid，
如果你需要调用微信的API，则你需要返回全部参数。
如果你在在公众平台官网的开发者中心处设置了消息加密，则你还需要返回aeskey，
但目前消息加解密的功能还尚未实现。

.. code-block:: python

    @wechat.config_getter
    def get_config(id):
        return dict(
            appid="appid",
            appsecret="appsecret",
            token="token"
        ) if id=="demo" else dict()
        
    
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

被装饰函数接收一个参数:ref:`WeChatRequest`对象，返回一个:ref:`WeChatResponse`对象。

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
    
    def callback(sender, identify, **kwargs):
        logging.info("{identify} sent response: {response}"\
            .format(identity=identity, response=kwargs["response"]))
    
    signals.response_sent.connect(callback, wechat)
    
信号的发送者为WeChat扩展实例，信号将至少接收一个identity参数，暨访问者自定义的公众号id。
在本例中，我们注册了回复已发送的信号。该信号发送于已接收到微信请求，并且成功回复以后。
不包括微信请求异常（Bad Request）回复的状况，但包含控制器抛出未经处理的异常的状况。

注意，使用信号需要安装blinker模块。

关于信号的详细说明，可以参考 :ref:`signal`章节。


请求微信API
=================

*** 尚未进行单元测试 ***