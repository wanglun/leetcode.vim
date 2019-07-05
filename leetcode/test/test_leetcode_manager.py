import unittest
from unittest.mock import patch, MagicMock, Mock

from leetcode import leetcode_manager


@patch('leetcode.leetcode_manager.cache', autospec=True)
@patch('leetcode.leetcode_manager.leetcode_client', autospec=True)
class LeetCodeManagerTest(unittest.TestCase):

    def test_login(self, mock_client: MagicMock, _):
        leetcode_manager.login('u', 'p')
        mock_client.login.assert_called_once_with('u', 'p')

    def test_get_problem_list(self, mock_client: MagicMock,
                              mock_cache: MagicMock):
        mock_result = Mock()
        mock_cache.load_problem_list.return_value = None
        mock_client.get_problem_list.return_value = mock_result

        problem_list = leetcode_manager.get_problem_list()

        self.assertEqual(problem_list, mock_result)
        mock_cache.save_problem_list.assert_called()

    def test_get_cached_problem_list(self, _, mock_cache: MagicMock):
        mock_result = Mock()
        mock_cache.load_problem_list.return_value = mock_result

        problem_list = leetcode_manager.get_problem_list()

        self.assertEqual(problem_list, mock_result)
        mock_cache.save_problem_list.assert_not_called()

    def test_get_problem(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_client.get_problem.return_value = mock_result

        problem = leetcode_manager.get_problem('title-slug')

        self.assertEqual(problem, mock_result)
        mock_client.get_problem.assert_called_once_with('title-slug')

    def test_get_submission_list(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_client.get_submission_list.return_value = mock_result

        submission_list = leetcode_manager.get_submission_list('title-slug')

        self.assertEqual(submission_list, mock_result)
        mock_client.get_submission_list.assert_called_once_with('title-slug')

    def test_get_submission(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_client.get_submission.return_value = mock_result

        submission_list = leetcode_manager.get_submission('12345')

        self.assertEqual(submission_list, mock_result)
        mock_client.get_submission.assert_called_once_with('12345')

    def test_test_code(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_request = Mock()
        mock_client.test_code.return_value = mock_result

        test_job = leetcode_manager.test_code(mock_request)

        self.assertEqual(test_job, mock_result)
        mock_client.test_code.assert_called_once_with(mock_request)

    def test_submit_code(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_request = Mock()
        mock_client.submit_code.return_value = mock_result

        submission_id = leetcode_manager.submit_code(mock_request)

        self.assertEqual(submission_id, mock_result)
        mock_client.submit_code.assert_called_once_with(mock_request)

    def test_retrieve_test_result(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_client.retrieve_test_result.return_value = mock_result

        result = leetcode_manager.retrieve_test_result('id')

        self.assertEqual(result, mock_result)
        mock_client.retrieve_test_result.assert_called_once_with('id')

    def test_retrieve_submission_result(self, mock_client: MagicMock, _):
        mock_result = Mock()
        mock_client.retrieve_submission_result.return_value = mock_result

        result = leetcode_manager.retrieve_submission_result('id')

        self.assertEqual(result, mock_result)
        mock_client.retrieve_submission_result.assert_called_once_with('id')
