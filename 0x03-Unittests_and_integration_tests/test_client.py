#!/usr/bin/env python3
""" unit test for client module"""

import unittest
from unittest.mock import patch
from parameterized import parameterized

from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """ A github org client test unit test module"""

    @parameterized.expand((
        "google",
        "abc",
    ))
    @patch("client.get_json")
    def test_org(self, org_name, mock_get):
        """Function that test the org method of GithubOrgClient"""
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
        """function to test the public repos url property"""

        test_client = GithubOrgClient()

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=unittest.mock.PropertyMock
        ) as mock_property:
            mock_property.return_value = "test"

            self.assertEqual(test_client._public_repos_url, "test")

    @patch('client.get_json')
    def test_public_repos(self, mocked_get_json):
        """method to test the public_repos method"""

        test_payload = [
            {
                "id": 1,
                "name": "repo-a",
                "full_name": "test-org/repo-a",
                "private": False,
                "owner": {"login": "test-org"},
            },
            {
                "id": 2,
                "name": "repo-b",
                "full_name": "test-org/repo-b",
                "private": False,
                "owner": {"login": "test-org"},
            },
        ]
        mocked_get_json.return_value = test_payload

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=unittest.mock.PropertyMock
        ) as mock_property:
            mock_property.return_value = \
                "https://api.github.com/orgs/test-org/repos"

            test_client = GithubOrgClient("test-org")

            result = test_client.public_repos(license=None)

            self.assertEqual(result, ["repo-a", "repo-b"])

            mocked_get_json.assert_called_once_with(
                f"https://api.github.com/orgs/test-org/repos"
                )

            result1 = test_client._public_repos_url
            self.assertEqual(
                result1,
                "https://api.github.com/orgs/test-org/repos"
                )

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, test_repo, test_key, expected):
        """test for the has_license method"""
        test_client = GithubOrgClient('test-org')

        self.assertEqual(
            test_client.has_license(test_repo, test_key),
            expected
        )


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Testing inegration of the GihubOrgClient"""
    @classmethod
    def setUp(self):
        pass

    @classmethod
    def tearDown(self):
        pass
