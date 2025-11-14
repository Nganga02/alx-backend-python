#!/usr/bin/env python3
""" unit test for client module"""

import unittest
from unittest.mock import patch
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """ A github org client test unit test module
    """
    # @classmethod
    # def setUp(self):
    #     self.test_client = GithubOrgClient()

    # @classmethod
    # def tearDown(self):
    #     self.test_client.dispose()
    
    @parameterized.expand((
        "google",
        "abc",
    ))
    @patch("client.get_json")
    def test_org(self, org_name, mock_get):
        """Function that test the org method of GithubOrgClient 
        """
        mock_get.return_value = {"org": org_name, "data": "test"}

        test_client = GithubOrgClient(org_name)
        org_data = test_client.org
        self.assertEqual(
            org_data,
            {"org": org_name, "data": "test"}
        )

        mock_get.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

        self.assertEqual(org_data, {"org": org_name, "data": "test"})

    def test_public_repos_url(self):
        """function to test the public repos url property
        """

        test_client = GithubOrgClient()
        
        with patch.object(
            test_client,
            '_public_repos_url',
            new_callable=unittest.mock.PropertyMock
        ) as mock_property:
            mock_property.return_value = "test"

            self.assertEqual(test_client._public_repos_url, "test")