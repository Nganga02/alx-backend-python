import unittest
from parameterized import parameterized

from utils import access_nested_map


class TestAccessNextedMap(unittest.TestCase):
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}},("a",), {"b": 2}),
        ({"a": {"b": 2}},("a", "b"), 2),
    ])
    def test_access_nested_map(self, nestedMap, path, expected):
        self.assertEqual(access_nested_map(nested_map=nestedMap, path=path), expected)