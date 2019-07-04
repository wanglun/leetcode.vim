from functools import wraps
import time
import unittest

from leetcode import leetcode_client, messages
from leetcode.exception import LeetCodeOperationFailureError
from leetcode.types import Difficulty, TestResult, SubmissionRequest, \
    SubmissionResult


def retry_if_too_fast(test_method):
    @wraps(test_method)
    def wrapped_test_method(*args, **kwargs):
        retry_count = 0

        while retry_count < 5:
            try:
                time.sleep(5)
                return test_method(*args, **kwargs)
            except LeetCodeOperationFailureError as exn:
                if messages.TOO_FAST in str(exn):
                    retry_count += 1
                else:
                    raise exn

    return wrapped_test_method


class LeetCodeClientIntegrationTest(unittest.TestCase):

    USERNAME = 'travisjohn'
    PASSWORD = 'bexqaf-zokric-3nEzfi'

    MAX_RETRY_COUNT = 20

    DATA_INPUT = '[3,2,2,3]\n3'

    ACCEPTED_CODE = '''
class Solution(object):
    def removeElement(self, nums, val):
        i = 0
        for j in range(len(nums)):
            if nums[j] != val:
                nums[i] = nums[j]
                i += 1
        del nums[i:]
'''

    CORRECT_ANSWER = ['[2,2]']

    SYNTAX_ERROR_CODE = 'class Solution(object'

    WRONG_ANSWER_CODE = '''
class Solution(object):
    def removeElement(self, nums, val):
        i = 0
        for j in range(len(nums)):
            if nums[j] == val:
                nums[i] = nums[j]
                i += 1
        del nums[i:]
'''

    WRONG_ANSWER = ['[3,3]']



    @classmethod
    def setUpClass(cls):
        leetcode_client.login(cls.USERNAME, cls.PASSWORD)

    def test_get_problem_list(self):
        problem_list = leetcode_client.get_problem_list()

        self.assertTrue(len(problem_list) > 0)

        found = False

        for problem in problem_list:
            if problem.title_slug == 'two-sum':
                self.assertEqual(problem.question_id, '1')
                self.assertEqual(problem.difficulty, Difficulty.EASY)
                self.assertFalse(problem.paid_only)
                found = True
                break

        self.assertTrue(found)

    def test_get_problem(self):
        problem = leetcode_client.get_problem('two-sum')
        self.assertEqual(problem.title, 'Two Sum')
        self.assertEqual(problem.question_id, '1')
        self.assertEqual(problem.difficulty, Difficulty.EASY)
        self.assertIn('indices', problem.description)
        self.assertIn('cpp', problem.templates)

    def test_get_submission_list(self):
        submission_list = leetcode_client.get_submission_list('two-sum')

        self.assertTrue(len(submission_list) > 0)

        found = False

        for submission in submission_list:
            if submission.id == '240646655':
                self.assertEqual(submission.lang, 'python')
                self.assertEqual(submission.status, 'Accepted')
                self.assertEqual(submission.runtime, '4768 ms')
                self.assertEqual(submission.memory, '12.8 MB')
                found = True
                break

        self.assertTrue(found)

    def test_get_submission(self):
        submission = leetcode_client.get_submission('240646655')

        self.assertEqual(submission.id, '240646655')
        self.assertEqual(submission.lang, 'python')
        self.assertEqual(submission.problem_id, '1')
        self.assertEqual(submission.passed, '29')
        self.assertEqual(submission.total, '29')
        self.assertEqual(submission.status, 'Accepted')
        self.assertEqual(submission.runtime, '4768 ms')
        self.assertGreater(submission.runtime_percentile, 10)
        self.assertLess(submission.runtime_percentile, 40)

    def _poll_test_result(self, job_id: str) -> TestResult:
        retry_count = 0

        while retry_count < self.MAX_RETRY_COUNT:
            result = leetcode_client.retrieve_test_result(job_id)

            if isinstance(result, TestResult):
                return result

            time.sleep(1)
            retry_count += 1

        raise RuntimeError('Code execution timed out')

    @retry_if_too_fast
    def test_test_accepted_code(self):
        request = SubmissionRequest(
            problem_id='27',
            title_slug='remove-element',
            lang='python',
            data_input=self.DATA_INPUT,
            code=self.ACCEPTED_CODE,
        )

        time.sleep(3)

        test_job = leetcode_client.test_code(request)

        result = self._poll_test_result(test_job.actual_id)
        self.assertEqual(result.status, 'Accepted')
        self.assertEqual(result.answer, self.CORRECT_ANSWER)
        self.assertEqual(result.stdout, [])
        self.assertEqual(result.errors, [])

        expected = self._poll_test_result(test_job.expected_id)
        self.assertEqual(expected.status, 'Accepted')
        self.assertEqual(expected.answer, self.CORRECT_ANSWER)
        self.assertEqual(expected.stdout, [])
        self.assertEqual(result.errors, [])

    @retry_if_too_fast
    def test_test_code_with_compile_error(self):
        request = SubmissionRequest(
            problem_id='27',
            title_slug='remove-element',
            lang='python',
            data_input=self.DATA_INPUT,
            code=self.SYNTAX_ERROR_CODE,
        )

        test_job = leetcode_client.test_code(request)

        result = self._poll_test_result(test_job.actual_id)
        self.assertEqual(result.status, 'Compile Error')
        self.assertEqual(result.answer, [])
        self.assertEqual(result.stdout, [])

        found = False

        for error in result.errors:
            if 'invalid syntax' in error:
                found = True
                break

        self.assertTrue(found)

    @retry_if_too_fast
    def test_test_code_with_wrong_answer(self):
        request = SubmissionRequest(
            problem_id='27',
            title_slug='remove-element',
            lang='python',
            data_input=self.DATA_INPUT,
            code=self.WRONG_ANSWER_CODE,
        )

        test_job = leetcode_client.test_code(request)

        result = self._poll_test_result(test_job.actual_id)
        # The status is Accepted even if the answer is wrong.
        self.assertEqual(result.status, 'Accepted')
        self.assertEqual(result.answer, self.WRONG_ANSWER)
        self.assertEqual(result.stdout, [])
        self.assertEqual(result.errors, [])

    def _poll_submission_result(self, submission_id: str) -> SubmissionResult:
        retry_count = 0

        while retry_count < self.MAX_RETRY_COUNT:
            result = leetcode_client.retrieve_submission_result(submission_id)

            if isinstance(result, SubmissionResult):
                return result

            time.sleep(1)
            retry_count += 1

        raise RuntimeError('Code execution timed out')

    @retry_if_too_fast
    def test_submit_accepted_code(self):
        request = SubmissionRequest(
            problem_id='27',
            title_slug='remove-element',
            lang='python',
            data_input=self.DATA_INPUT,
            code=self.ACCEPTED_CODE
        )

        submission_id = leetcode_client.submit_code(request)

        result = self._poll_submission_result(submission_id)

        self.assertEqual(result.status, 'Accepted')
        self.assertIn('ms', result.runtime)
        self.assertIn('MB', result.memory)
        self.assertGreater(result.runtime_percentile, 0)
        self.assertLess(result.runtime_percentile, 100)
        self.assertGreater(result.memory_percentile, 0)
        self.assertLess(result.memory_percentile, 100)

    @retry_if_too_fast
    def test_submit_wrong_answer_code(self):
        request = SubmissionRequest(
            problem_id='27',
            title_slug='remove-element',
            lang='python',
            data_input=self.DATA_INPUT,
            code=self.WRONG_ANSWER_CODE,
        )

        submission_id = leetcode_client.submit_code(request)

        result = self._poll_submission_result(submission_id)

        self.assertEqual(result.status, 'Wrong Answer')
        self.assertEqual('N/A', result.runtime)
        self.assertEqual('N/A', result.memory)
        self.assertNotEqual(result.expected_answer, result.actual_answer)
        self.assertIsNotNone(result.data_input)
