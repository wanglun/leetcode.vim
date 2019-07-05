from typing import List, Union

from leetcode import cache, leetcode_client
from leetcode.types import Problem, ProblemDetail, SubmissionDetail, TestJob, \
    Submission, RunningSubmission, SubmissionResult, SubmissionRequest, \
    TestResult


def login(username: str, password: str) -> None:
    leetcode_client.login(username, password)


def get_problem_list() -> List[Problem]:
    cached_problem_list = cache.load_problem_list()
    if cached_problem_list is not None:
        return cached_problem_list

    new_problem_list = leetcode_client.get_problem_list()
    cache.save_problem_list(new_problem_list)
    return new_problem_list


def get_problem(title_slug: str) -> ProblemDetail:
    return leetcode_client.get_problem(title_slug)


def get_submission_list(title_slug: str) -> List[Submission]:
    return leetcode_client.get_submission_list(title_slug)


def get_submission(submission_id: str) -> SubmissionDetail:
    return leetcode_client.get_submission(submission_id)


def test_code(request: SubmissionRequest) -> TestJob:
    return leetcode_client.test_code(request)


def submit_code(request: SubmissionRequest) -> str:
    return leetcode_client.submit_code(request)


def retrieve_test_result(test_id: str) -> Union[RunningSubmission, TestResult]:
    return leetcode_client.retrieve_test_result(test_id)


def retrieve_submission_result(submission_id: str) \
        -> Union[RunningSubmission, SubmissionResult]:
    return leetcode_client.retrieve_submission_result(submission_id)
