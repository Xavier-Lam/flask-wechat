#encoding:utf8

from xml.etree import ElementTree

from . import XMLElementBase

class WeChatResponseSubElement(dict, XMLElementBase):
    def __init__(self, d):
        super(WeChatResponseSubElement, self).__init__(d)
        for k, v in d.items():
            setattr(self, k, v)
    
class WeChatResponseSubList(list, XMLElementBase):
    def serialize(self, parent):
        cls = SubElement(**self.__fields__)
        rv = "<" + self.__tag__ + ">"
        for item in self:
            rv += cls(item).serialize(ele)
        rv += "</" + self.__tag__ + ">"
        return rv

def SubElement(**fields):
    return type("WeChatResponseSubElement", 
        (WeChatResponseSubElement, ), dict(__fields__=fields))
    
def SubList(name, fields):
    return type("WeChatResponseSubList", 
        (WeChatResponseSubList, ), dict(__tag__=name, __fields__=fields))