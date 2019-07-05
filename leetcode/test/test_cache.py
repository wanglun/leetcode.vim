from copy import deepcopy
from datetime import datetime, timedelta
import io
import pickle
import unittest
from unittest.mock import patch, MagicMock

from leetcode import cache
from leetcode.cache import CachedData
from leetcode.types import Problem, ProblemState, Difficulty


class NoCloseIO(io.BytesIO):
    def close(self):
        pass


@patch('leetcode.cache.os')
@patch('leetcode.cache.open')
class CacheTest(unittest.TestCase):

    CACHED_DATA = CachedData(
        version=cache.CACHE_VERSION,
        expired_at=datetime.now() + timedelta(days=1),
        problem_list=[
            Problem(
                state=ProblemState.AC,
                question_id='2',
                frontend_question_id='2',
                title='Three Sum',
                title_slug='three-sum',
                paid_only=True,
                ac_rate=0.93,
                difficulty=Difficulty.MEDIUM,
                frequency=None,
                time_period_frequency=None,
            )
        ]
    )

    def test_delete_cache(self, _, mock_os: MagicMock):
        mock_os.access.return_value = True
        cache.delete_cache()
        mock_os.remove.assert_called_once()

    def test_delete_cache_no_action(self, _, mock_os: MagicMock):
        mock_os.access.return_value = False
        cache.delete_cache()
        mock_os.remove.assert_not_called()

    def test_load_problem_list(self, mock_open: MagicMock, mock_os: MagicMock):
        mock_os.access.return_value = True
        cache_file = io.BytesIO(
            pickle.dumps(self.CACHED_DATA,
                         protocol=pickle.HIGHEST_PROTOCOL))
        mock_open.return_value = cache_file

        problem_list = cache.load_problem_list()
        assert problem_list is not None
        self.assertEqual(len(problem_list), 1)
        self.assertEqual(problem_list[0].title_slug, 'three-sum')

    def test_load_problem_list_no_file(self, _, mock_os: MagicMock):
        mock_os.access.return_value = False
        problem_list = cache.load_problem_list()
        self.assertEqual(problem_list, None)

    def test_load_problem_list_expired(self, mock_open: MagicMock,
                                       mock_os: MagicMock):
        mock_os.access.return_value = True

        cached_data = deepcopy(self.CACHED_DATA)
        cached_data.expired_at = datetime.now() - timedelta(days=1)

        cache_file = io.BytesIO(
            pickle.dumps(cached_data, protocol=pickle.HIGHEST_PROTOCOL))
        mock_open.return_value = cache_file

        problem_list = cache.load_problem_list()
        self.assertEqual(problem_list, None)
        mock_os.remove.assert_called_once()

    def test_save_problem_list(self, mock_open: MagicMock, mock_os: MagicMock):
        mock_os.access.return_value = False

        cache_file = NoCloseIO()
        mock_open.return_value = cache_file

        assert self.CACHED_DATA.problem_list is not None
        cache.save_problem_list(self.CACHED_DATA.problem_list)

        mock_os.makedirs.assert_called_once()

        cached_data: CachedData = pickle.loads(cache_file.getvalue())

        assert cached_data.problem_list is not None
        self.assertEqual(cached_data.problem_list[0].title_slug, 'three-sum')
