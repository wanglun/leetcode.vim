from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

from leetcode.test.utils import load_test_data, load_test_json
from leetcode.submission import get_submission, get_submission_list, \
    Submission, SubmissionDetail, SubmissionStatus


@patch('leetcode.submission.session')
class SubmissionTest(unittest.TestCase):

    def test_get_submission_list(self, mock_session: MagicMock):
        submission_list_data = load_test_json('submission_list.json')

        mock_session.post.return_value.status_code = 200
        mock_session.post.return_value.json.return_value = submission_list_data

        submission_list = get_submission_list('two-sum')

        expected_submission = Submission(
            id='238743927',
            time=datetime.fromtimestamp(1561532073),
            lang='cpp',
            runtime='116 ms',
            memory='9.2 MB',
            status=SubmissionStatus.ACCEPTED,
        )

        self.assertEqual(submission_list[0], expected_submission)

    def test_get_accepted_submission(self, mock_session: MagicMock):
        submission_data = load_test_data('accepted_submission.html')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.text = submission_data

        submission = get_submission('69630365')

        expected_submission = SubmissionDetail(
            id='69630365',
            status=SubmissionStatus.ACCEPTED,
            runtime='343 ms',
            passed='16',
            total='Attribute not found',
            data_input='Attribute not found',
            actual_answer='Attribute not found',
            expected_answer='Attribute not found',
            problem_id='1',
            title_slug='two-sum',
            lang='cpp',
            code='class Solution {\r\n};',
            runtime_percentile=1.3946,
        )

        self.assertEqual(submission, expected_submission)

    def test_get_wrong_submission(self, mock_session: MagicMock):
        submission_data = load_test_data('wrong_submission.html')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.text = submission_data

        submission = get_submission('240141910')

        expected_submission = SubmissionDetail(
            id='240141910',
            status=SubmissionStatus.WRONG_ANSWER,
            runtime='N/A',
            passed='0',
            total='29',
            data_input='[2,7,11,15]\n9',
            actual_answer='[0,0]',
            expected_answer='[0,1]',
            problem_id='1',
            title_slug='two-sum',
            lang='cpp',
            code='class Solution {\npublic:\n};',
            runtime_percentile=94.604,
        )

        self.assertEqual(submission, expected_submission)
