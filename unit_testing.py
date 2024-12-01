import unittest
import repos_module

class TestSuite(unittest.TestCase):
    def test_num_repos(self):
        pass

    def test_repo_instance(self):
        self.assertIsInstance(self, repos_module.GitHubRepository)

    def test_status_code(self, response_code):
        self.assertEqual(response_code, 200, msg=f"Error status code, impossible to access page ಠ_ಠ: {response_code}")

    def check_rate_limit(self, rate_remaining):
        self.assertGreater(rate_remaining, 0, msg="Rate Limit Exceeded, try again later.")

    def check_pull_request_args(self, **kwargs):
        self.assertGreaterEqual(len(kwargs), 11, "Not enough information found in keyword arguments.")

    def check_author_args(self, **kwargs):
        self.assertGreaterEqual(len(kwargs), 5, "Not enough information found in keyword arguments.")