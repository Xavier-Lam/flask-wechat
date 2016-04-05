#encoding:utf8

from . import BaseTest
from ..data import data

import flask_wechat.filters as filters 
from flask_wechat.messages import *

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
        
        view_filter = filters.event.view
        
        self.assertTrue(view_filter()(message)==True)
        self.assertTrue(view_filter(message)==True)
        self.assertTrue(view_filter(correct)(message)==True)
        self.assertTrue(view_filter(correct_part)(message)==True)
        self.assertFalse(view_filter(wrong)(message)==True)
        
        self.assertFalse(view_filter(correct_part, True)(message)==True)
        self.assertTrue(view_filter(correct, True)(message)==True)
        self.assertFalse(view_filter(wrong, True)(message)==True)
        
        self.assertTrue(
            view_filter(correct_part_wrong_case, False, True)(message)==True)
        self.assertTrue(
            view_filter(correct_wrong_case, False, True)(message)==True)
        self.assertTrue(view_filter(correct, False, True)(message)==True)
        self.assertFalse(view_filter(wrong, False, True)(message)==True)
            
        self.assertFalse(
            view_filter(correct_part_wrong_case, False, False)(message)==True)
        self.assertFalse(
            view_filter(correct_wrong_case, False, False)(message)==True)
        self.assertTrue(view_filter(correct_part, False, False)(message)==True)
        self.assertTrue(view_filter(correct, False, False)(message)==True)
        self.assertFalse(view_filter(wrong, False, False)(message)==True)
            
        self.assertFalse(
            view_filter(correct_part_wrong_case, True, True)(message)==True)
        self.assertTrue(
            view_filter(correct_wrong_case, True, True)(message)==True)
        self.assertFalse(
            view_filter(correct_part, True, True)(message)==True)
        self.assertTrue(view_filter(correct, True, True)(message)==True)
        self.assertFalse(view_filter(wrong, True, True)(message)==True)
            
            
    def test_3_event_click(self):
        message = self.messages["event_click"]
        eventkey = self.messages["event_click"].eventkey
        self.assertTrue(filters.event.click()(message)==True)
        self.assertTrue(filters.event.click(message)==True)
        self.assertTrue(
            filters.event.click(eventkey)(message)==True)
        self.assertFalse(
            filters.event.click(eventkey + "1")(message)==True)
            
    def test_4_message_location(self):
        message = self.messages["message_location"]
        self.assertFalse(filters.message.location(
            message.location_x+1, message.location_y+1, 1)(message)==True)
        self.assertTrue(filters.message.location(
            message.location_x+1, message.location_y+1, 2)(message)==True)
        
    def test_5_message_text(self):
        pass
        
    def test_6_message_others(self):
        self.assertTrue(
            filters.message.typeof("image")(self.messages["message_pic"])==True)
        self.assertTrue(
            filters.message.image(self.messages["message_pic"])==True)
        self.assertFalse(
            filters.message.image(self.messages["message_voice"])==True)
        self.assertTrue(
            filters.message.voice(self.messages["message_voice"])==True)
        self.assertTrue(
            filters.message.video(self.messages["message_video"])==True)
        self.assertTrue(
            filters.message.shortvideo(self.messages["message_shortvideo"])==True)
        
    def test_7_common_filter(self):
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