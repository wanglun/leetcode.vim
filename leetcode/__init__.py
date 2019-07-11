import logging

from leetcode.problem import get_problem, get_problem_list
from leetcode.run_code import test_code, retrieve_test_result, submit_code, \
    retrieve_submission_result
from leetcode.session import login
from leetcode.submission import get_submission, get_submission_list
from leetcode.utils import wrap_call

log = logging.getLogger(__name__)

log.setLevel(logging.ERROR)


def enable_debug_logging():
    file_handler = logging.FileHandler('leetcode-vim.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)
