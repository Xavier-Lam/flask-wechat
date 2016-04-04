
.. _filter:

=========================
 过滤器
=========================

过滤器在@wechat.handler 装饰器中使用，作为@wechat.handler 的第二个参数传入。
亦可将多个过滤器合成一个数组（list）传入。


预定义过滤器
================

预定义过滤器通过

.. code-block:: python
    
    from flask.ext.wechat import filters
    
引入。

预定义过滤器包括：

事件过滤器
---------------

- 过滤事件 

.. code-block:: python

    filters.event
    
直接使用（无需括号）过滤所有事件消息。

- 过滤指定事件 

.. code-block:: python

    filters.event(event)
    
传入事件名字符串，过滤符合该事件名的消息。


- 过滤关注事件 

.. code-block:: python

    filters.event.subscribe
    
    
- 过滤取消关注事件 

.. code-block:: python

    filters.event.unsubscribe


- 过滤点击事件 

.. code-block:: python

    filters.event.click
    

- 过滤指定点击事件 

.. code-block:: python

    filters.event.click(key)
    
过滤key为字符串key的点击事件


- 过滤跳转事件 

.. code-block:: python

    filters.event.view
    

- 过滤指定跳转事件 

.. code-block:: python

    filters.event.view(url, accuracy=False, ignorecase=False)
    
过滤url为字符串url的跳转事件，
可选参数accuracy表示是否精准匹配，默认否，
ignorecase是否区分大小写，默认否。


消息过滤器
--------------


逻辑过滤器
--------------

- 默认过滤器 

.. code-block:: python

    filters.all

所有消息都会成功进入该过滤器。
该过滤器优先级最低，只有在无法匹配其他过滤器的情况下才会匹配该过滤器。

- 且过滤器 

.. code-block:: python

    filters.and_(*funcs)
    
传入多个过滤器，只有符合所有过滤器要求的情况下，才能进入控制器。
一旦有过滤器不符合条件，不再执行funcs中的下一过滤器（与and 相同）。

- 或过滤器 

.. code-block:: python

    filters.or_(*funcs)
    
传入多个过滤器，在符合任一过滤器的情况下，就会进入过滤器。


自定义过滤器
========================

你可以编写自定义过滤器。过滤器接收一个 :ref:`WeChatRequest` 对象。
返回True代表符合条件，False代表不符合条件。