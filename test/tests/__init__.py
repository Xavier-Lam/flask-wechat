#encoding: utf8
from unittest import TestCase

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