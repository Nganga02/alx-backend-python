#!/usr/bin/env python3
""" A Github org client test unit test module
"""

import unittest
from unittest.mock import patch
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """ A github org client test unit test module
    """
    
    @parameterized.expand((
        "google",
        "abc",
    ))
    @patch("client.requests.get")
    def test_org(self, org_name, mock_get):
        """Function that test the org method of GithubOrgClient 
        """
        mock_get.return_value.json.return_value = {"{}".format(org_name): "This is the map"}
        test_client = GithubOrgClient(org_name)
        test_client.org
        self.assertEqual(test_client.org, {"{}".format(org_name): "This is the map"})

        mock_get.assert_called_once()