import unittest
from unittest.mock import patch, MagicMock

from leetcode.test.utils import load_test_json
from leetcode.run_code import test_code, submit_code, retrieve_test_result, \
    retrieve_submission_result, SubmissionRequest, TestJob, RunningSubmission, \
    SubmissionResult, TestResult
from leetcode.submission import SubmissionStatus


@patch('leetcode.run_code.session')
class RunCodeTest(unittest.TestCase):

    def test_test_code(self, mock_session: MagicMock):
        test_job_data = load_test_json('test_job.json')

        mock_session.post.return_value.status_code = 200
        mock_session.post.return_value.json.return_value = test_job_data

        request = SubmissionRequest(
            problem_id='1',
            title_slug='two-sum',
            lang='python',
            code='somecodehere',
            data_input='[1,2,3,4]\n3',
        )

        test_job = test_code(request)

        expected_body = {
            'question_id': '1',
            'data_input': '[1,2,3,4]\n3',
            'lang': 'python',
            'typed_code': 'somecodehere',
            'judge_type': 'small'
        }

        _, kwargs = mock_session.post.call_args
        self.assertEqual(kwargs['json'], expected_body)

        expected_test_job = TestJob(
            actual_id='interpret_1562042312.8283226_Bp2cNlWQo9',
            expected_id='interpret_expected_1562039275.1088336_vSrCbZvbai',
        )

        self.assertEqual(test_job, expected_test_job)

    def test_submit_code(self, mock_session: MagicMock):
        expected_id = 1234567

        mock_session.post.return_value.status_code = 200
        mock_session.post.return_value.json.return_value = {
            'submission_id': expected_id,
        }

        request = SubmissionRequest(
            problem_id='1',
            title_slug='two-sum',
            lang='python',
            code='somecodehere',
            data_input='[1,2,3,4]\n3',
        )

        submission_id = submit_code(request)

        expected_body = {
            'question_id': '1',
            'lang': 'python',
            'typed_code': 'somecodehere',
        }

        _, kwargs = mock_session.post.call_args
        self.assertEqual(kwargs['json'], expected_body)

        self.assertEqual(submission_id, str(expected_id))

    def test_retrieve_pending_test_result(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {'state': 'PENDING'}

        result = retrieve_test_result('test-id')

        self.assertEqual(result, RunningSubmission(state='PENDING'))

    def test_retrieve_started_test_result(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {'state': 'STARTED'}

        result = retrieve_test_result('test-id')

        self.assertEqual(result, RunningSubmission(state='STARTED'))

    def test_retrieve_good_test_result(self, mock_session: MagicMock):
        check_data = load_test_json('check_good_test.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = check_data

        result = retrieve_test_result('test-id')

        expected_result = TestResult(
            status=SubmissionStatus.ACCEPTED,
            answer=['[0,1]'],
            runtime='16 ms',
            errors=[],
            stdout=['ok'],
        )

        self.assertEqual(result, expected_result)

    def test_retrieve_compile_error_test_result(self, mock_session: MagicMock):
        check_data = load_test_json('check_compile_error_test.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = check_data

        result = retrieve_test_result('test-id')

        expected_result = TestResult(
            status=SubmissionStatus.COMPILE_ERROR,
            answer=[],
            runtime='N/A',
            errors=['Line 4: SyntaxError: invalid syntax'],
            stdout=[],
        )

        self.assertEqual(result, expected_result)

    def test_retrieve_timeout_test_result(self, mock_session: MagicMock):
        check_data = load_test_json('check_timeout_test.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = check_data

        result = retrieve_test_result('test-id')

        expected_result = TestResult(
            status=SubmissionStatus.TIME_LIMIT_EXCEEDED,
            answer=[],
            runtime='N/A',
            errors=[],
            stdout=['ok', 'test'],
        )

        self.assertEqual(result, expected_result)

    def test_retrieve_wrong_answer_submission_result(
            self, mock_session: MagicMock):

        check_data = load_test_json('check_wrong_answer_submission.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = check_data

        result = retrieve_submission_result('submission-id')

        expected_result = SubmissionResult(
            status=SubmissionStatus.WRONG_ANSWER,
            lang='python',
            runtime='N/A',
            memory='N/A',
            errors=[],
            stdout='ok\ntest',
            data_input='[3,2,4]\n6',
            actual_answer='[0,1]',
            expected_answer='[1,2]',
        )

        self.assertEqual(result, expected_result)

    def test_retrieve_accepted_submission_result(self, mock_session: MagicMock):
        check_data = load_test_json('check_accepted_submission.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = check_data

        result = retrieve_submission_result('submission-id')

        expected_result = SubmissionResult(
            status=SubmissionStatus.ACCEPTED,
            lang='cpp',
            runtime='112 ms',
            memory='9.1 MB',
            errors=[],
            stdout='',
            actual_answer='',
            runtime_percentile=39.703400000000016,
            memory_percentile=97.15320000000001,
        )

        self.assertEqual(result, expected_result)
