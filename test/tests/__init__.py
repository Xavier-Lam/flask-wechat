#encoding: utf8
from hashlib import sha1
import time
from unittest import TestCase

from ..app import app

__all__ = ["BaseTest", "TestContext"]

class TestContext:
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

class BaseTest(TestCase):
    """
    base class of tests
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass
        
class ClientTest(BaseTest):
    identity = "test"
    
    def setUp(self):
        super(ClientTest, self).setUp()
        
    def create_request(self, data, content_type="text/xml"):
        return self.app.post(self.posturl + self._query_str, 
                data=data, content_type=content_type)
                
    @property
    def _query_str(self):
        nonce = "12345678"
        timestamp = str(int(time.time()))
        token = self.token
        arr = [token, timestamp, nonce]
        arr.sort()
        string = "".join(arr)
        sign = sha1(string.encode()).hexdigest()
        return "?nonce={nonce}&timestamp={timestamp}&signature={sign}".format(
            nonce = nonce,
            timestamp = timestamp,
            sign=sign
        )

from .apiclient import ApiClientTestCases
from .filter import FilterTestCases
from .response import ResponseTestCases
from .serialize import SerializeTestCases
from .signal import SignalTestCases