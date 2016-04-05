#encoding:utf8

from xml.etree import ElementTree

from . import XMLElementBase

class WeChatResponseSubElement(dict, XMLElementBase):
    def __init__(self, d):
        super(WeChatResponseSubElement, self).__init__(d)
        for k, v in d.items():
            setattr(self, k, v)
    
class WeChatResponseSubList(list, XMLElementBase):
    def __init__(self, l):
        cls = SubElement(**self.__fields__)
        new_list = [cls(item) for item in l]
        super(WeChatResponseSubList, self).__init__(new_list)
            
    def serialize(self, parent=None):
        rv = ""
        for item in self:
            rv += "<" + self.__tag__ + ">"
            rv += item.serialize(self)
            rv += "</" + self.__tag__ + ">"
        return rv

def SubElement(**fields):
    return type("WeChatResponseSubElement", 
        (WeChatResponseSubElement, ), dict(__fields__=fields))
    
def SubList(name, fields):
    return type("WeChatResponseSubList", 
        (WeChatResponseSubList, ), dict(__tag__=name, __fields__=fields))