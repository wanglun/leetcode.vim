import unittest
from unittest.mock import patch, MagicMock

from leetcode.exception import LeetCodeOperationFailureError
from leetcode.session import login


@patch('leetcode.session._session')
class SessionTest(unittest.TestCase):

    def test_login(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.post.return_value.status_code = 302

        login('user', 'pass')

    def test_login_error(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.post.return_value.status_code = 400

        self.assertRaises(LeetCodeOperationFailureError,
                          lambda: login('user', 'pass'))
