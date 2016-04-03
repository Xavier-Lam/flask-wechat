#encoding:utf8

from . import BaseTest
from ..data import data

import wechat.filters as filters 
from wechat.messages import *

class SignalTestCases(BaseTest):
    def setUp(self):
        super(FilterTestCases, self).setUp()
        pass