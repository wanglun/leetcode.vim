from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

from leetcode import leetcode_client
from leetcode.exception import LeetCodeOperationFailureError
from leetcode.test.utils import load_test_data, load_test_json
from leetcode.types import ProblemState, Difficulty, Problem, ProblemDetail, \
    Submission, SubmissionDetail, SubmissionRequest, TestJob, \
    RunningSubmission, TestResult, SubmissionResult
from leetcode.third_party import dataclass


@dataclass
class MockResponse:
    status_code: int
    text: str


@patch('leetcode.leetcode_client._session')
class LeetCodeClientTest(unittest.TestCase):

    def test_login(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.post.return_value.status_code = 302

        leetcode_client.login('user', 'pass')

    def test_login_error(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.post.return_value.status_code = 400

        self.assertRaises(LeetCodeOperationFailureError,
                          lambda: leetcode_client.login('user', 'pass'))

    def test_get_problem_list(self, mock_session: MagicMock):
        api_problems_all = load_test_json('api_problems_all.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = api_problems_all

        problem_list = leetcode_client.get_problem_list()

        self.assertEqual(len(problem_list), 10)

        problem = problem_list[0]

        expected_problem = Problem(
            state=ProblemState.NEW,
            question_id='1198',
            frontend_question_id='1098',
            title='Unpopular Books',
            title_slug='unpopular-books',
            paid_only=True,
            ac_rate=148/303,
            difficulty=Difficulty.MEDIUM,
            frequency=0,
            time_period_frequency=None,
        )

        self.assertEqual(problem, expected_problem)

    def test_get_problem(self, mock_session: MagicMock):
        question_data = load_test_json('question.json')
        question = question_data['data']['question']

        mock_session.post.return_value.status_code = 200
        mock_session.post.return_value.json.return_value = question_data

        problem = leetcode_client.get_problem('two-sum')

        expected_problem = ProblemDetail(
            question_id='1',
            frontend_question_id='1',
            title='Two Sum',
            title_slug='two-sum',
            paid_only=False,
            difficulty=Difficulty.EASY,
            description=question['content'],
            templates={'cpp': question['codeSnippets'][0]['code']},
            testable=True,
            testcase='[2,7,11,15]\n9',
            total_accepted='1.9M',
            total_submission='4.3M',
            ac_rate='44.3%',
            likes=11072,
            dislikes=376,
        )

        self.assertEqual(problem, expected_problem)

    def test_get_submission_list(self, mock_session: MagicMock):
        submission_list_data = load_test_json('submission_list.json')

        mock_session.post.return_value.status_code = 200
        mock_session.post.return_value.json.return_value = submission_list_data

        submission_list = leetcode_client.get_submission_list('two-sum')

        expected_submission = Submission(
            id='238743927',
            time=datetime.fromtimestamp(1561532073),
            lang='cpp',
            runtime='116 ms',
            memory='9.2 MB',
            status='Accepted',
        )

        self.assertEqual(submission_list[0], expected_submission)

    def test_get_accepted_submission(self, mock_session: MagicMock):
        submission_data = load_test_data('accepted_submission.html')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.text = submission_data

        submission = leetcode_client.get_submission('69630365')

        expected_submission = SubmissionDetail(
            id='69630365',
            status='Accepted',
            runtime='343 ms',
            passed='16',
            total='Not found',
            data_input='Not found',
            actual_answer='Not found',
            expected_answer='Not found',
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

        submission = leetcode_client.get_submission('240141910')

        expected_submission = SubmissionDetail(
            id='240141910',
            status='Wrong Answer',
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

        test_job = leetcode_client.test_code(request)

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

        submission_id = leetcode_client.submit_code(request)

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

        result = leetcode_client.retrieve_test_result('test-id')

        self.assertEqual(result, RunningSubmission(state='PENDING'))

    def test_retrieve_started_test_result(self, mock_session: MagicMock):
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {'state': 'STARTED'}

        result = leetcode_client.retrieve_test_result('test-id')

        self.assertEqual(result, RunningSubmission(state='STARTED'))

    def test_retrieve_good_test_result(self, mock_session: MagicMock):
        check_data = load_test_json('check_good_test.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = check_data

        result = leetcode_client.retrieve_test_result('test-id')

        expected_result = TestResult(
            status='Accepted',
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

        result = leetcode_client.retrieve_test_result('test-id')

        expected_result = TestResult(
            status='Compile Error',
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

        result = leetcode_client.retrieve_test_result('test-id')

        expected_result = TestResult(
            status='Time Limit Exceeded',
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

        result = leetcode_client.retrieve_submission_result('submission-id')

        expected_result = SubmissionResult(
            status='Wrong Answer',
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

        result = leetcode_client.retrieve_submission_result('submission-id')

        expected_result = SubmissionResult(
            status='Accepted',
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
