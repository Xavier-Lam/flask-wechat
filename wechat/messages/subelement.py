#encoding:utf8

from xml.etree import ElementTree

class WeChatResponseSubElement(dict):
    pass
    
class WeChatResponseSubList(list):
    def serialize(self, parent, return_=False):
        cls = SubElement(**self.__fields__)
        for item in self:
            ele = ElementTree.SubElement(parent, self.__tag__)
            cls(item).serialize(ele, False)
        if return_:
            return ElementTree.tostring(parent, "unicode", "xml")

def SubElement(**fields):
    return type("WeChatResponseSubElement", 
        (WeChatResponseSubElement, ), dict(__fields__=fields))
    
def SubList(name, fields):
    return type("WeChatResponseSubList", 
        (WeChatResponseSubList, ), dict(__tag__=name, __fields__=fields))