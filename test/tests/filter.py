#encoding:utf8

from . import BaseTest
from ..data import data

import wechat.filters as filters 
from wechat.messages import *

class FilterTestCases(BaseTest):
    messages = dict()

    def setUp(self):
        super(FilterTestCases, self).setUp()
        for message_type, message in data.items():
            if message_type.startswith("event"):
                self.messages[message_type] = WeChatEvent(**message)
            elif message_type.startswith("message"):
                self.messages[message_type] = WeChatMessage(**message)

    def test_1_event_subscribe(self):
        self.assertTrue(filters.event.subscribe(self.messages["event_subscribe"]))
        self.assertFalse(filters.event.subscribe(self.messages["event_click"]))
        
    def test_2_event_view(self):
        message = self.messages["event_view"]
    
        correct = message.eventkey
        correct_part = correct[1:3]
        correct_part_wrong_case = correct_part.upper()
        correct_wrong_case = correct.upper()
        wrong = correct + "111"
        
        self.assertTrue(filters.event.view()(message))
        self.assertTrue(filters.event.view(correct)(message))
        self.assertTrue(filters.event.view(correct_part)(message))
        self.assertFalse(filters.event.view(wrong)(message))
        
        self.assertFalse(filters.event.view(correct_part, True)(message))
        self.assertTrue(filters.event.view(correct, True)(message))
        self.assertFalse(filters.event.view(wrong, True)(message))
        
        self.assertTrue(filters.event.view(correct_part_wrong_case,
            False, True)(message))
        self.assertTrue(filters.event.view(correct_wrong_case,
            False, True)(message))
        self.assertTrue(filters.event.view(correct, False, True)(message))
        self.assertFalse(filters.event.view(wrong, False, True)(message))
            
        self.assertFalse(filters.event.view(correct_part_wrong_case,
            False, False)(message))
        self.assertFalse(filters.event.view(correct_wrong_case,
            False, False)(message))
        self.assertTrue(filters.event.view(correct_part,
            False, False)(message))
        self.assertTrue(filters.event.view(correct, False, False)(message))
        self.assertFalse(filters.event.view(wrong, False, False)(message))
            
        self.assertFalse(filters.event.view(correct_part_wrong_case,
            True, True)(message))
        self.assertTrue(filters.event.view(correct_wrong_case,
            True, True)(message))
        self.assertFalse(filters.event.view(correct_part,
            True, True)(message))
        self.assertTrue(filters.event.view(correct, True, True)(message))
        self.assertFalse(filters.event.view(wrong, True, True)(message))
            
            
    def test_3_event_click(self):
        message = self.messages["event_click"]
        self.assertTrue(filters.event.click()(message))
        self.assertTrue(filters.event.click(self.messages["event_click"].eventkey)\
            (message))
        self.assertFalse(filters.event.click(self.messages["event_click"].eventkey + "1")\
            (message))
        
    def test_4_message_others(self):
        self.assertTrue(filters.message.typeof("image")(self.messages["message_pic"]))
        self.assertTrue(filters.message.image(self.messages["message_pic"]))
        self.assertFalse(filters.message.image(self.messages["message_voice"]))
        self.assertTrue(filters.message.voice(self.messages["message_voice"]))
        self.assertTrue(filters.message.video(self.messages["message_video"]))
        self.assertTrue(filters.message.shortvideo(self.messages["message_shortvideo"]))
        
    def test_5_message_text(self):
        pass
        
    def test_6_common_filter(self):
        t = lambda m: True
        f = lambda m: False
        m = self.messages["event_click"]
        
        self.assertTrue(filters.all(m))
        
        self.assertTrue(filters.or_(t, t)(m)==True)
        self.assertTrue(filters.or_(f, t)(m)==True)
        self.assertTrue(filters.or_(t, f)(m)==True)
        self.assertFalse(filters.or_(f, f)(m)==True)
        self.assertTrue(filters.or_(t, t, t)(m)==True)
        self.assertTrue(filters.or_(t, t, f)(m)==True)
        self.assertTrue(filters.or_(t, f, t)(m)==True)
        self.assertTrue(filters.or_(t, f, f)(m)==True)
        self.assertTrue(filters.or_(f, t, t)(m)==True)
        self.assertTrue(filters.or_(f, t, f)(m)==True)
        self.assertTrue(filters.or_(f, f, t)(m)==True)
        self.assertFalse(filters.or_(f, f, f)(m)==True)
        
        self.assertTrue(filters.and_(t, t)(m)==True)
        self.assertFalse(filters.and_(t, f)(m)==True)
        self.assertFalse(filters.and_(f, t)(m)==True)
        self.assertFalse(filters.and_(f, f)(m)==True)
        self.assertTrue(filters.and_(t, t, t)(m)==True)
        self.assertFalse(filters.and_(t, t, f)(m)==True)
        self.assertFalse(filters.and_(t, f, t)(m)==True)
        self.assertFalse(filters.and_(t, f, f)(m)==True)
        self.assertFalse(filters.and_(f, t, t)(m)==True)
        self.assertFalse(filters.and_(f, t, f)(m)==True)
        self.assertFalse(filters.and_(f, f, t)(m)==True)
        self.assertFalse(filters.and_(f, f, f)(m)==True)