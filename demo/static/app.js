(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// Copyright Joyent, Inc. and other Node contributors.
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the
// "Software"), to deal in the Software without restriction, including
// without limitation the rights to use, copy, modify, merge, publish,
// distribute, sublicense, and/or sell copies of the Software, and to permit
// persons to whom the Software is furnished to do so, subject to the
// following conditions:
//
// The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
// OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
// NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
// DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
// USE OR OTHER DEALINGS IN THE SOFTWARE.

function EventEmitter() {
  this._events = this._events || {};
  this._maxListeners = this._maxListeners || undefined;
}
module.exports = EventEmitter;

// Backwards-compat with node 0.10.x
EventEmitter.EventEmitter = EventEmitter;

EventEmitter.prototype._events = undefined;
EventEmitter.prototype._maxListeners = undefined;

// By default EventEmitters will print a warning if more than 10 listeners are
// added to it. This is a useful default which helps finding memory leaks.
EventEmitter.defaultMaxListeners = 10;

// Obviously not all Emitters should be limited to 10. This function allows
// that to be increased. Set to zero for unlimited.
EventEmitter.prototype.setMaxListeners = function(n) {
  if (!isNumber(n) || n < 0 || isNaN(n))
    throw TypeError('n must be a positive number');
  this._maxListeners = n;
  return this;
};

EventEmitter.prototype.emit = function(type) {
  var er, handler, len, args, i, listeners;

  if (!this._events)
    this._events = {};

  // If there is no 'error' event listener then throw.
  if (type === 'error') {
    if (!this._events.error ||
        (isObject(this._events.error) && !this._events.error.length)) {
      er = arguments[1];
      if (er instanceof Error) {
        throw er; // Unhandled 'error' event
      }
      throw TypeError('Uncaught, unspecified "error" event.');
    }
  }

  handler = this._events[type];

  if (isUndefined(handler))
    return false;

  if (isFunction(handler)) {
    switch (arguments.length) {
      // fast cases
      case 1:
        handler.call(this);
        break;
      case 2:
        handler.call(this, arguments[1]);
        break;
      case 3:
        handler.call(this, arguments[1], arguments[2]);
        break;
      // slower
      default:
        args = Array.prototype.slice.call(arguments, 1);
        handler.apply(this, args);
    }
  } else if (isObject(handler)) {
    args = Array.prototype.slice.call(arguments, 1);
    listeners = handler.slice();
    len = listeners.length;
    for (i = 0; i < len; i++)
      listeners[i].apply(this, args);
  }

  return true;
};

EventEmitter.prototype.addListener = function(type, listener) {
  var m;

  if (!isFunction(listener))
    throw TypeError('listener must be a function');

  if (!this._events)
    this._events = {};

  // To avoid recursion in the case that type === "newListener"! Before
  // adding it to the listeners, first emit "newListener".
  if (this._events.newListener)
    this.emit('newListener', type,
              isFunction(listener.listener) ?
              listener.listener : listener);

  if (!this._events[type])
    // Optimize the case of one listener. Don't need the extra array object.
    this._events[type] = listener;
  else if (isObject(this._events[type]))
    // If we've already got an array, just append.
    this._events[type].push(listener);
  else
    // Adding the second element, need to change to array.
    this._events[type] = [this._events[type], listener];

  // Check for listener leak
  if (isObject(this._events[type]) && !this._events[type].warned) {
    if (!isUndefined(this._maxListeners)) {
      m = this._maxListeners;
    } else {
      m = EventEmitter.defaultMaxListeners;
    }

    if (m && m > 0 && this._events[type].length > m) {
      this._events[type].warned = true;
      console.error('(node) warning: possible EventEmitter memory ' +
                    'leak detected. %d listeners added. ' +
                    'Use emitter.setMaxListeners() to increase limit.',
                    this._events[type].length);
      if (typeof console.trace === 'function') {
        // not supported in IE 10
        console.trace();
      }
    }
  }

  return this;
};

EventEmitter.prototype.on = EventEmitter.prototype.addListener;

EventEmitter.prototype.once = function(type, listener) {
  if (!isFunction(listener))
    throw TypeError('listener must be a function');

  var fired = false;

  function g() {
    this.removeListener(type, g);

    if (!fired) {
      fired = true;
      listener.apply(this, arguments);
    }
  }

  g.listener = listener;
  this.on(type, g);

  return this;
};

// emits a 'removeListener' event iff the listener was removed
EventEmitter.prototype.removeListener = function(type, listener) {
  var list, position, length, i;

  if (!isFunction(listener))
    throw TypeError('listener must be a function');

  if (!this._events || !this._events[type])
    return this;

  list = this._events[type];
  length = list.length;
  position = -1;

  if (list === listener ||
      (isFunction(list.listener) && list.listener === listener)) {
    delete this._events[type];
    if (this._events.removeListener)
      this.emit('removeListener', type, listener);

  } else if (isObject(list)) {
    for (i = length; i-- > 0;) {
      if (list[i] === listener ||
          (list[i].listener && list[i].listener === listener)) {
        position = i;
        break;
      }
    }

    if (position < 0)
      return this;

    if (list.length === 1) {
      list.length = 0;
      delete this._events[type];
    } else {
      list.splice(position, 1);
    }

    if (this._events.removeListener)
      this.emit('removeListener', type, listener);
  }

  return this;
};

EventEmitter.prototype.removeAllListeners = function(type) {
  var key, listeners;

  if (!this._events)
    return this;

  // not listening for removeListener, no need to emit
  if (!this._events.removeListener) {
    if (arguments.length === 0)
      this._events = {};
    else if (this._events[type])
      delete this._events[type];
    return this;
  }

  // emit removeListener for all listeners on all events
  if (arguments.length === 0) {
    for (key in this._events) {
      if (key === 'removeListener') continue;
      this.removeAllListeners(key);
    }
    this.removeAllListeners('removeListener');
    this._events = {};
    return this;
  }

  listeners = this._events[type];

  if (isFunction(listeners)) {
    this.removeListener(type, listeners);
  } else if (listeners) {
    // LIFO order
    while (listeners.length)
      this.removeListener(type, listeners[listeners.length - 1]);
  }
  delete this._events[type];

  return this;
};

EventEmitter.prototype.listeners = function(type) {
  var ret;
  if (!this._events || !this._events[type])
    ret = [];
  else if (isFunction(this._events[type]))
    ret = [this._events[type]];
  else
    ret = this._events[type].slice();
  return ret;
};

EventEmitter.prototype.listenerCount = function(type) {
  if (this._events) {
    var evlistener = this._events[type];

    if (isFunction(evlistener))
      return 1;
    else if (evlistener)
      return evlistener.length;
  }
  return 0;
};

EventEmitter.listenerCount = function(emitter, type) {
  return emitter.listenerCount(type);
};

function isFunction(arg) {
  return typeof arg === 'function';
}

function isNumber(arg) {
  return typeof arg === 'number';
}

function isObject(arg) {
  return typeof arg === 'object' && arg !== null;
}

function isUndefined(arg) {
  return arg === void 0;
}

},{}],2:[function(require,module,exports){
/**
 * Copyright (c) 2014-2015, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 */

module.exports.Dispatcher = require('./lib/Dispatcher');

},{"./lib/Dispatcher":3}],3:[function(require,module,exports){
(function (process){
/**
 * Copyright (c) 2014-2015, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 *
 * @providesModule Dispatcher
 * 
 * @preventMunge
 */

'use strict';

exports.__esModule = true;

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError('Cannot call a class as a function'); } }

var invariant = require('fbjs/lib/invariant');

var _prefix = 'ID_';

/**
 * Dispatcher is used to broadcast payloads to registered callbacks. This is
 * different from generic pub-sub systems in two ways:
 *
 *   1) Callbacks are not subscribed to particular events. Every payload is
 *      dispatched to every registered callback.
 *   2) Callbacks can be deferred in whole or part until other callbacks have
 *      been executed.
 *
 * For example, consider this hypothetical flight destination form, which
 * selects a default city when a country is selected:
 *
 *   var flightDispatcher = new Dispatcher();
 *
 *   // Keeps track of which country is selected
 *   var CountryStore = {country: null};
 *
 *   // Keeps track of which city is selected
 *   var CityStore = {city: null};
 *
 *   // Keeps track of the base flight price of the selected city
 *   var FlightPriceStore = {price: null}
 *
 * When a user changes the selected city, we dispatch the payload:
 *
 *   flightDispatcher.dispatch({
 *     actionType: 'city-update',
 *     selectedCity: 'paris'
 *   });
 *
 * This payload is digested by `CityStore`:
 *
 *   flightDispatcher.register(function(payload) {
 *     if (payload.actionType === 'city-update') {
 *       CityStore.city = payload.selectedCity;
 *     }
 *   });
 *
 * When the user selects a country, we dispatch the payload:
 *
 *   flightDispatcher.dispatch({
 *     actionType: 'country-update',
 *     selectedCountry: 'australia'
 *   });
 *
 * This payload is digested by both stores:
 *
 *   CountryStore.dispatchToken = flightDispatcher.register(function(payload) {
 *     if (payload.actionType === 'country-update') {
 *       CountryStore.country = payload.selectedCountry;
 *     }
 *   });
 *
 * When the callback to update `CountryStore` is registered, we save a reference
 * to the returned token. Using this token with `waitFor()`, we can guarantee
 * that `CountryStore` is updated before the callback that updates `CityStore`
 * needs to query its data.
 *
 *   CityStore.dispatchToken = flightDispatcher.register(function(payload) {
 *     if (payload.actionType === 'country-update') {
 *       // `CountryStore.country` may not be updated.
 *       flightDispatcher.waitFor([CountryStore.dispatchToken]);
 *       // `CountryStore.country` is now guaranteed to be updated.
 *
 *       // Select the default city for the new country
 *       CityStore.city = getDefaultCityForCountry(CountryStore.country);
 *     }
 *   });
 *
 * The usage of `waitFor()` can be chained, for example:
 *
 *   FlightPriceStore.dispatchToken =
 *     flightDispatcher.register(function(payload) {
 *       switch (payload.actionType) {
 *         case 'country-update':
 *         case 'city-update':
 *           flightDispatcher.waitFor([CityStore.dispatchToken]);
 *           FlightPriceStore.price =
 *             getFlightPriceStore(CountryStore.country, CityStore.city);
 *           break;
 *     }
 *   });
 *
 * The `country-update` payload will be guaranteed to invoke the stores'
 * registered callbacks in order: `CountryStore`, `CityStore`, then
 * `FlightPriceStore`.
 */

var Dispatcher = (function () {
  function Dispatcher() {
    _classCallCheck(this, Dispatcher);

    this._callbacks = {};
    this._isDispatching = false;
    this._isHandled = {};
    this._isPending = {};
    this._lastID = 1;
  }

  /**
   * Registers a callback to be invoked with every dispatched payload. Returns
   * a token that can be used with `waitFor()`.
   */

  Dispatcher.prototype.register = function register(callback) {
    var id = _prefix + this._lastID++;
    this._callbacks[id] = callback;
    return id;
  };

  /**
   * Removes a callback based on its token.
   */

  Dispatcher.prototype.unregister = function unregister(id) {
    !this._callbacks[id] ? process.env.NODE_ENV !== 'production' ? invariant(false, 'Dispatcher.unregister(...): `%s` does not map to a registered callback.', id) : invariant(false) : undefined;
    delete this._callbacks[id];
  };

  /**
   * Waits for the callbacks specified to be invoked before continuing execution
   * of the current callback. This method should only be used by a callback in
   * response to a dispatched payload.
   */

  Dispatcher.prototype.waitFor = function waitFor(ids) {
    !this._isDispatching ? process.env.NODE_ENV !== 'production' ? invariant(false, 'Dispatcher.waitFor(...): Must be invoked while dispatching.') : invariant(false) : undefined;
    for (var ii = 0; ii < ids.length; ii++) {
      var id = ids[ii];
      if (this._isPending[id]) {
        !this._isHandled[id] ? process.env.NODE_ENV !== 'production' ? invariant(false, 'Dispatcher.waitFor(...): Circular dependency detected while ' + 'waiting for `%s`.', id) : invariant(false) : undefined;
        continue;
      }
      !this._callbacks[id] ? process.env.NODE_ENV !== 'production' ? invariant(false, 'Dispatcher.waitFor(...): `%s` does not map to a registered callback.', id) : invariant(false) : undefined;
      this._invokeCallback(id);
    }
  };

  /**
   * Dispatches a payload to all registered callbacks.
   */

  Dispatcher.prototype.dispatch = function dispatch(payload) {
    !!this._isDispatching ? process.env.NODE_ENV !== 'production' ? invariant(false, 'Dispatch.dispatch(...): Cannot dispatch in the middle of a dispatch.') : invariant(false) : undefined;
    this._startDispatching(payload);
    try {
      for (var id in this._callbacks) {
        if (this._isPending[id]) {
          continue;
        }
        this._invokeCallback(id);
      }
    } finally {
      this._stopDispatching();
    }
  };

  /**
   * Is this Dispatcher currently dispatching.
   */

  Dispatcher.prototype.isDispatching = function isDispatching() {
    return this._isDispatching;
  };

  /**
   * Call the callback stored with the given id. Also do some internal
   * bookkeeping.
   *
   * @internal
   */

  Dispatcher.prototype._invokeCallback = function _invokeCallback(id) {
    this._isPending[id] = true;
    this._callbacks[id](this._pendingPayload);
    this._isHandled[id] = true;
  };

  /**
   * Set up bookkeeping needed when dispatching.
   *
   * @internal
   */

  Dispatcher.prototype._startDispatching = function _startDispatching(payload) {
    for (var id in this._callbacks) {
      this._isPending[id] = false;
      this._isHandled[id] = false;
    }
    this._pendingPayload = payload;
    this._isDispatching = true;
  };

  /**
   * Clear bookkeeping used for dispatching.
   *
   * @internal
   */

  Dispatcher.prototype._stopDispatching = function _stopDispatching() {
    delete this._pendingPayload;
    this._isDispatching = false;
  };

  return Dispatcher;
})();

module.exports = Dispatcher;
}).call(this,require('_process'))
},{"_process":5,"fbjs/lib/invariant":4}],4:[function(require,module,exports){
(function (process){
/**
 * Copyright 2013-2015, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 *
 * @providesModule invariant
 */

"use strict";

/**
 * Use invariant() to assert state which your program assumes to be true.
 *
 * Provide sprintf-style format (only %s is supported) and arguments
 * to provide information about what broke and what you were
 * expecting.
 *
 * The invariant message will be stripped in production, but the invariant
 * will remain to ensure logic does not differ in production.
 */

var invariant = function (condition, format, a, b, c, d, e, f) {
  if (process.env.NODE_ENV !== 'production') {
    if (format === undefined) {
      throw new Error('invariant requires an error message argument');
    }
  }

  if (!condition) {
    var error;
    if (format === undefined) {
      error = new Error('Minified exception occurred; use the non-minified dev environment ' + 'for the full error message and additional helpful warnings.');
    } else {
      var args = [a, b, c, d, e, f];
      var argIndex = 0;
      error = new Error('Invariant Violation: ' + format.replace(/%s/g, function () {
        return args[argIndex++];
      }));
    }

    error.framesToPop = 1; // we don't care about invariant's own frame
    throw error;
  }
};

module.exports = invariant;
}).call(this,require('_process'))
},{"_process":5}],5:[function(require,module,exports){
// shim for using process in browser

var process = module.exports = {};
var queue = [];
var draining = false;
var currentQueue;
var queueIndex = -1;

function cleanUpNextTick() {
    draining = false;
    if (currentQueue.length) {
        queue = currentQueue.concat(queue);
    } else {
        queueIndex = -1;
    }
    if (queue.length) {
        drainQueue();
    }
}

function drainQueue() {
    if (draining) {
        return;
    }
    var timeout = setTimeout(cleanUpNextTick);
    draining = true;

    var len = queue.length;
    while(len) {
        currentQueue = queue;
        queue = [];
        while (++queueIndex < len) {
            if (currentQueue) {
                currentQueue[queueIndex].run();
            }
        }
        queueIndex = -1;
        len = queue.length;
    }
    currentQueue = null;
    draining = false;
    clearTimeout(timeout);
}

process.nextTick = function (fun) {
    var args = new Array(arguments.length - 1);
    if (arguments.length > 1) {
        for (var i = 1; i < arguments.length; i++) {
            args[i - 1] = arguments[i];
        }
    }
    queue.push(new Item(fun, args));
    if (queue.length === 1 && !draining) {
        setTimeout(drainQueue, 0);
    }
};

// v8 likes predictible objects
function Item(fun, array) {
    this.fun = fun;
    this.array = array;
}
Item.prototype.run = function () {
    this.fun.apply(null, this.array);
};
process.title = 'browser';
process.browser = true;
process.env = {};
process.argv = [];
process.version = ''; // empty string to avoid regexp issues
process.versions = {};

function noop() {}

process.on = noop;
process.addListener = noop;
process.once = noop;
process.off = noop;
process.removeListener = noop;
process.removeAllListeners = noop;
process.emit = noop;

process.binding = function (name) {
    throw new Error('process.binding is not supported');
};

process.cwd = function () { return '/' };
process.chdir = function (dir) {
    throw new Error('process.chdir is not supported');
};
process.umask = function() { return 0; };

},{}],6:[function(require,module,exports){
var Dispatcher = require('../dispatchers/appdispatcher');

var MessageActions = {
	sendMessage: function(type, value) {
		Dispatcher.dispatch({
			actionType: "MESSAGE_SEND",
			type: type,
			value: value
		});
	},

	receiveMessage: function(messageObject) {
		Dispatcher.dispatch({
			actionType: "MESSAGE_RECEIVED",
			message: messageObject
		});
	}
};

module.exports = MessageActions;

},{"../dispatchers/appdispatcher":19}],7:[function(require,module,exports){
var Dispatcher = require('../dispatchers/appdispatcher');

var MenuActions = {
	trigger: function(info) {
		Dispatcher.dispatch({
			actionType: "MENU_TRIGGER",
			params: info.params,
			sender: info.sender
		});
	}
};

module.exports = MenuActions;

},{"../dispatchers/appdispatcher":19}],8:[function(require,module,exports){
var Dispatcher = require('../dispatchers/appdispatcher');

var MessageActions = {
	sendMessage: function(type, value) {
		Dispatcher.dispatch({
			actionType: "MESSAGE_SEND",
			type: type,
			value: value
		});
	},

	receiveMessage: function(messageObject) {
		Dispatcher.dispatch({
			actionType: "MESSAGE_RECEIVED",
			message: messageObject
		});
	}
};

module.exports = MessageActions;

},{"../dispatchers/appdispatcher":19}],9:[function(require,module,exports){
var Footer = require("./components/footer");
var Storyboard = require("./components/storyboard");

// var App = React.createClass({
// 	renderer: function() {}
// });

ReactDOM.render(
	(React.createElement("div", {className: "app"}, 
		React.createElement(Storyboard, null), 
		React.createElement(Footer, null)
	)),
	document.getElementById("example")
);

},{"./components/footer":13,"./components/storyboard":18}],10:[function(require,module,exports){
var MessageActions = require("../actions/messageactions");

var Input = React.createClass({displayName: "Input",
	render: function() {
		return (React.createElement("form", {onSubmit: this.handleSubmit}, 
				React.createElement("input", {name: "input", onKeyDown: this.handleKeyDown, ref: "input", placeholder: "请输入文字"}), 
				React.createElement("button", null)
			))
	},

	handleKeyDown: function(e) {
		if(e.key==="return") {
			this.handleSubmit(e);
		}
	},

	handleSubmit: function(e) {
		e.preventDefault();
		var value = this.refs.input.value.trim().toString();
		if(value) {
			this.refs.input.value = "";
			MessageActions.sendMessage("text", value);
		}
	},
});

module.exports = Input;

},{"../actions/messageactions":8}],11:[function(require,module,exports){
var MenuItem = require("./menuitem");

var MenuStore = require("../stores/menustore");

var Menu = React.createClass({displayName: "Menu",
	render: function() {
		return (React.createElement("div", {className: "menu"}, 
			
				this.getMainMenu().map(function(o) {
					return React.createElement(MenuItem, {bind: o, title: o.name})
				})
			
			));
	},

	getMainMenu: function() {
		return MenuStore.getAll() || [];
	}
});

module.exports = Menu;

},{"../stores/menustore":21,"./menuitem":14}],12:[function(require,module,exports){
var ToggleButton = React.createClass({displayName: "ToggleButton",
	render: function() {
		return React.createElement("a", {className: "toggle-button", onClick: this.handleClick});
	},

	handleClick: function(e) {
		this.props.onChange();
	}
});

module.exports = ToggleButton;

},{}],13:[function(require,module,exports){
var Input = require("./Input");
var Menu = require("./Menu");
var ToggleButton = require("./ToggleButton");

var Footer = React.createClass({displayName: "Footer",
	getInitialState: function() {
		return {
			showMenu: false
		};
	},

	render: function() {
		return (React.createElement("div", {className: "footer"}, 
				React.createElement(ToggleButton, {onChange: this.handleToggleButtonChange}), 
				React.createElement("div", {className: "interactive"}, 
				 this.state.showMenu? React.createElement(Menu, null): React.createElement(Input, null)
				)
			));
	},

	handleToggleButtonChange: function() {
		this.setState({showMenu: !this.state.showMenu});
	}
});

module.exports = Footer;

},{"./Input":10,"./Menu":11,"./ToggleButton":12}],14:[function(require,module,exports){
var MenuActions = require("../actions/menuactions");

var MenuItem = React.createClass({displayName: "MenuItem",
	getDefaultProps: function() {
		return {
			active: false
		};
	},

	getInitialState: function() {
		return {
			active: this.props.active
		};
	},

	render: function() {
		var classes = ["menu-item"];
		if(this.state.active) {
			classes.push("active");
		}
		if(this.getCanExtends()) {
			classes.push("hassub");
		}
		var bind = this.props.bind;
		return (React.createElement("div", {className: classes.join(" "), onClick: this.handleClick}, 
					React.createElement("span", {className: "header"}, this.props.title), 
					
						this.getCanExtends()? React.createElement("span", {className: "extends"}, " "): null, 
					
					
						this.getCanExtends()? React.createElement("div", {className: "submenu " + (this.state.active?"active": "")}, 
							bind.sub_button.list.map(function(o) {
								return React.createElement(MenuItem, {bind: o, title: o.name});
							})
						): null
					
			));
	},

	handleClick: function(e) {
		if(this.getCanExtends()) {
			this.setState({active: !this.state.active});
		} else {
			MenuActions.trigger({
				sender: this,
				params: this.props.bind
			});
		}
	},

	getCanExtends: function() {
		return !!this.props.bind.sub_button;
	}
});

module.exports = MenuItem;

},{"../actions/menuactions":7}],15:[function(require,module,exports){
var ImageMessage = require("./messages/imagemessage");
var TextMessage = require("./messages/textmessage");

var messageMap = {
	"image": ImageMessage,
	"text": TextMessage
};

var Message = React.createClass({displayName: "Message",
	render: function() {
		return (React.createElement("div", {className: "message-container"}, 
				this.createMessageElement()
			));
	},

	createMessageElement: function() {
		var message = this.props.message;
		var source = this.getMessageSource();
		if(source!="public") {
			return (React.createElement("div", {className: source + " message"}, 
					React.createElement("image", {className: "avatar"}), 
					React.createElement(TextMessage, {source: source, content: message.content})
				));
		} else {
			console.log(1);
		}
	},

	getMessageSource: function() {
		var message = this.props.message;
		return message.publicMessage? "public":
			message.fromUserName? "theirs": "mine";
	}
});

module.exports = Message;

},{"./messages/imagemessage":16,"./messages/textmessage":17}],16:[function(require,module,exports){
var ImageMessage = React.createClass({displayName: "ImageMessage",
	render: function() {
		return (React.createElement("div", {className: "message image"}, 
				React.createElement("img", {src: this.props.picurl})
			));
	}
});

module.exports = ImageMessage;

},{}],17:[function(require,module,exports){
var TextMessage = React.createClass({displayName: "TextMessage",
	render: function() {
		return React.createElement("div", {className: "detail text"}, this.props.content);
	}
});

module.exports = TextMessage;

},{}],18:[function(require,module,exports){
var MessageStore = require("../stores/messagestore");

var Message = require("./message");

var Storyboard = React.createClass({displayName: "Storyboard",
	getInitialState: function() {
		return {
			messages: MessageStore.getAll()
		}
	},

	componentDidMount: function() {
		MessageStore.addListener("change", this.handleChange);
	},

	componentDidUpdate: function() {
		var board = this.refs.storyboard;
		board.scrollTop = board.scrollHeight;
	},

	componentWillUnmount: function() {
		MessageStore.removeListener("change", this.handle);
	},

	render: function() {
		return (React.createElement("div", {className: "storyboard", ref: "storyboard"}, 
			
				this.state.messages.map(function(o) {
					return (React.createElement(Message, {message: o}));
				})
			
			));
	},

	handleChange: function() {
		this.setState({
			messages: MessageStore.getAll()
		});
	}
});

module.exports = Storyboard;

},{"../stores/messagestore":22,"./message":15}],19:[function(require,module,exports){
var Dispatcher = require('flux').Dispatcher;
module.exports = new Dispatcher();

},{"flux":2}],20:[function(require,module,exports){
var MessageActions = require("../actions/MessageActions");

var str1 = "<xml><ToUserName><![CDATA[toUser]]></ToUserName><FromUserName><![CDATA[fromUser]]></FromUserName><CreateTime>1348831860</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[";
var str2 = "]]></Content><MsgId>1234567890123456</MsgId></xml>";

var MessageService = {
	sendMessage: function(text) {
		$.ajax({
					url: "/wechat/callbacks/tmp/", 
					data: str1 + text + str2, 
					method: "POST",
					contentType: "text/xml",
					success: function(resp) {
						MessageActions.receiveMessage((new XMLSerializer()).serializeToString(resp).replace(/\n/g, ""));
					}});
	}
};

module.exports = MessageService;

},{"../actions/MessageActions":6}],21:[function(require,module,exports){
var EventEmitter = require('events').EventEmitter;

var MenuStore = Object.assign({}, EventEmitter.prototype, {
	items:  [ 
       { 
           "type": "click", 
           "name": "今日歌曲", 
           "key": "V1001_TODAY_MUSIC"
       }, 
       { 
           "name": "菜单", 
           "sub_button": { 
               "list": [ 
                   { 
                       "type": "view", 
                       "name": "搜索", 
                       "url": "http://www.soso.com/"
                   }, 
                   { 
                       "type": "view", 
                       "name": "视频", 
                       "url": "http://v.qq.com/"
                   }, 
                   { 
                       "type": "click", 
                       "name": "赞一下我们", 
                       "key": "V1001_GOOD"
                   }
               ]
           }
       }
   ],

	getAll: function() {
		return this.items;
	}
});

module.exports = MenuStore;

},{"events":1}],22:[function(require,module,exports){
var EventEmitter = require('events').EventEmitter;

var Dispatcher = require('../dispatchers/appdispatcher');

var MessageService = require("../services/message");

var MessageStore = Object.assign({}, EventEmitter.prototype, {
	items:  [{ 
       "fromUserName": "click", 
       "content": "今日歌曲", 
   }, { 
       "fromUserName": "click", 
       "content": "明日歌曲", 
   }, { 
       "fromUserName": "", 
       "content": "后日歌曲", 
   },],

	getAll: function() {
		return this.items;
	}
});

/* private methods */
var addMessage = function(source, content) {
  MessageStore.items.push({
    fromUserName: source,
    content: content
  });
  MessageStore.emit("change");
};

Dispatcher.register(function(action) {
  switch(action.actionType) {
    case "MESSAGE_SEND":
      addMessage("", action.value);
      MessageService.sendMessage(action.value);
      break;
    case "MESSAGE_RECEIVED":
      addMessage("theirs", action.message.match(/<Content><!\[CDATA\[(.+)\]\]><\/Content>/)[1]);
      break;
  }
});

module.exports = MessageStore;

},{"../dispatchers/appdispatcher":19,"../services/message":20,"events":1}]},{},[9]);
