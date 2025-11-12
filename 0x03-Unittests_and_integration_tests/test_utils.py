#!/usr/bin/env python3
import unittest
from parameterized import parameterized
from utils import access_nested_map

class TestAccessNestedMap(unittest.TestCase):
    """Class that inherits the TestCase class from python's unittest"""
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}},("a",), {"b": 2}),
        ({"a": {"b": 2}},("a", "b"), 2),
    ])
    def test_access_nested_map(self, nestedMap, path, expected):
        """function to test access_nested_map function"""
        self.assertEqual(access_nested_map(nested_map=nestedMap, path=path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1},("a", "b")),
    ])
    def test_access_nested_map_exception(self, nestedMap, path):
        """function used to test the function exception"""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map=nestedMap, path=path)