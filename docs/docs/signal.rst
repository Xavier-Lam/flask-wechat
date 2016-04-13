
.. _signal:

=========================
 信号
=========================

在Flask-WeChat 模块中，我们预定义了一些信号，用户可以监听这些信号，来了解一些变化，并执行相应逻辑。

你可以在代码中监听信号，所有信号的发送者都是WeChat 实例。以下是一个监听信号的简单示例。

.. code-block:: python
    
    def record(sender, identity, message, **kwargs):
        logging.info(str(message))
    request_deserialized.connect(record, wechat)
    
这段代码在wechat_granted


微信请求处理信号
---------------

处理微信请求时发出的信号，每个型号都包含一个identity参数，代表用户自定义的微信公众号id。


request_received
~~~~~~~~~~~~~~~~

接收到微信请求时触发。该信号包括以下参数

* identity

    前述公众号id
    
* request

    接收到的flask请求，类型是flask.Request
    

request_deserialized
~~~~~~~~~~~~~~~~~~~~

成功反序列化微信请求时触发，该信号包含以下参数

* identity

    前述公众号id
    
* message

    收到的微信消息，类型是flask.ext.wechat.messages.WeChatRequest


request_badrequest
~~~~~~~~~~~~~~~~~~

微信请求异常时触发，该信号包含以下参数

* identity

    前述公众号id
    
* request

    接收到的flask请求，类型是flask.Request
    
* message

    异常类型，包括 
    `incorrect timestamp` 时间戳格式错误。
    `incorrect args` url地址上未包含完整的参数，包括signature、timestamp、nonce等。
    `incorrect time` url上的timestamp超过服务器时间15分钟。
    `incorrect signature` 错误的签名，url上的签名结果与服务器计算的签名结果不符。
    `incorrect content` 无法将请求体反序列化为WeChatRequest。


request_handle_error
~~~~~~~~~~~~~~~~~~~~

业务逻辑处理微信请求时发生未经捕获的错误，该型号包含以下参数
    
* identity

    前述公众号id
    
* request

    接收到的flask请求，类型是flask.Request
    
* exception

    解析返回时捕获的异常


response_sent
~~~~~~~~~~~~~

送回请求时触发该信号，该信号包含以下参数

* identity

    前述公众号id
    
* request

    接收到的flask请求，类型是flask.Request
    
* response

    WeChatResponse实例或字符串



微信API处理信号
---------------

所有微信API处理信号都包含一个response参数与一个identity参数，
前者的类型是requests.Response，是微信服务器返回的对象。
后者的类型是str，是用户自定义的微信公众号id。


wechat_granted
~~~~~~~~~~~~~~

当公众号进行授权时或重新进行授权时会触发该信号。该信号包括以下参数

* response

    前述返回对象
    
* identity

    前述公众号id
    
* accesstoken

    授权获得的accesstoken
    
* expires_in

    授权获得的accesstoken在多久以后过期
    
理论上用户无需监听本信号，使用wechat.accesstoken 装饰函数即可获得同样效果。


wechat_servererror
~~~~~~~~~~~~~~~~~~

当微信服务器处理请求异常时触发该信号，异常包括但不仅包括服务器返回错误格式的数据。
该信号包含以下参数

* response

    前述返回对象
    
* identity

    前述公众号id
    
* exception

    解析返回时捕获的异常
    

wechat_error
~~~~~~~~~~~~

当请求返回错误时触发。该错误一般为客户端错误。该信号包含以下参数

* response

    前述返回对象
    
* identity

    前述公众号id
    
* code

    错误代码，可以通过错误代码在微信开发者文档中查询