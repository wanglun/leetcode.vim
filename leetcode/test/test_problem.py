import unittest
from unittest.mock import patch, MagicMock

from leetcode.test.utils import load_test_json
from leetcode.problem import get_problem, get_problem_list, ProblemState, \
    Difficulty, Problem, ProblemDetail


@patch('leetcode.problem.session')
class ProblemTest(unittest.TestCase):

    def test_get_problem_list(self, mock_session: MagicMock):
        api_problems_all = load_test_json('api_problems_all.json')

        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = api_problems_all

        problem_list = get_problem_list()

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

        problem = get_problem('two-sum')

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
