#encoding:utf8

from . import WeChatRequest

class WeChatEvent(WeChatRequest):
    __fields__ = dict(WeChatRequest.__fields__, **dict(
        Event=str,
        EventKey=str,
        Ticket=str
    ))

    _event = None

    @property
    def event(self):
        return self._event
        
    @event.setter
    def event(self, value):
        self._event = value
        
    def __repr__(self):
        return "<%s %s %s>"%(self.__class__.__name__, self.msgtype, self.event)