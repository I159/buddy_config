import unittest
from unittest import mock

from buddy_config import config


class TestTypes(unittest.TestCase):
    @mock.patch.dict("os.environ", {"BOOL_VALUE": "tRue"})
    def test_boolean_conversion(self):
        class MyConf(metaclass=config.Config):
            BOOL_VALUE = "BOOL_VALUE", bool

        conf = MyConf()
        self.assertTrue(conf.BOOL_VALUE)

    def test_default_boolean(self):
        class MyConf(metaclass=config.Config):
            BOOL_VALUE = "BOOL_VALUE", bool

        conf = MyConf(BOOL_VALUE=True)
        self.assertTrue(conf.BOOL_VALUE)

    def test_default_boolean_fail(self):
        class MyConf(metaclass=config.Config):
            BOOL_VALUE = "BOOL_VALUE", bool

        conf = MyConf(BOOL_VALUE=1.618)
        with self.assertRaises(ValueError):
            conf.BOOL_VALUE

    @mock.patch.dict("os.environ", {"BOOL_VALUE": "1234"})
    def test_non_convertable_custom_type(self):
        class MyConf(metaclass=config.Config):
            BOOL_VALUE = "BOOL_VALUE", bool

        conf = MyConf()
        with self.assertRaises(ValueError):
            conf.BOOL_VALUE
