#!/usr/bin/env python3


import unittest
from unittest.mock import patch
from parameterized import parameterized
from utils import (
    access_nested_map, 
    get_json,
    memoize
)


class TestAccessNestedMap(unittest.TestCase):
    """Class that inherits the TestCase class from python's unittest"""
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}},("a",), {"b": 2}),
        ({"a": {"b": 2}},("a", "b"), 2),
    ])
    def test_access_nested_map(self, nestedMap, path, expected):
        """
        Tests access_nested_map function
        tests if the function return the desired output;
        given the nested map and the path the function should return the expected results
        
        """
        self.assertEqual(access_nested_map(nested_map=nestedMap, path=path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1},("a", "b")),
    ])
    def test_access_nested_map_exception(self, nestedMap, path):
        """function used to test the function exception"""
        with self.assertRaises(KeyError):
            access_nested_map(nested_map=nestedMap, path=path)


class TestGetJson(unittest.TestCase):
    """Tests the utils.get_json function"""
    parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, payload):
        """Using unittest's mock to mock an external request so as to simulate http
        """
        with patch('utils.requests.get') as mocked_get:
            mocked_get.return_value.json() = payload
            
            response = get_json(url=test_url)
            response = get_json(url=test_url)
            mocked_get.assert_called_once_with(test_url)
            self.assertEqual(response, payload)



class TestMemoize(unittest.TestCase):
    """Class to test the utils.memoize decorator"""       
    def test_memoize():
        """Test the correct functioning of the memoize decorator"""

        class TestClass:

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()
            
        test_obj = TestClass() 
            
        with patch.object(TestClass, 'a_method', wraps=test_obj.a_method) as mocked_call:
            # calling the property twice so as to access the property
            test_obj.a_property
            test_obj.a_property

            """This ensures that the property is called once only"""
            mocked_call.assert_called_once()

