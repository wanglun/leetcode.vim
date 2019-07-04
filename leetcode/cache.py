from datetime import datetime, timedelta
import logging
import os
import os.path
import pickle
from typing import List, Optional

from leetcode import config
from leetcode.types import Problem
from leetcode.third_party import dataclass


CACHE_VERSION = 1


log = logging.getLogger(__name__)


@dataclass
class CachedData:
    version: int
    expired_at: datetime
    problem_list: Optional[List[Problem]] = None

    def update_expire_time(self):
        self.expired_at = \
            datetime.now() + timedelta(days=config.CACHE_EXPIRE_DAYS)


def delete_cache() -> None:
    if os.access(config.CACHE_PATH, os.F_OK):
        os.remove(config.CACHE_PATH)


def _new_cached_data() -> CachedData:
    return CachedData(
        version=CACHE_VERSION,
        expired_at=datetime.now() + timedelta(days=config.CACHE_EXPIRE_DAYS),
    )


def _load_cache() -> Optional[CachedData]:
    try:
        if not os.access(config.CACHE_PATH, os.F_OK):
            return None

        with open(config.CACHE_PATH, 'rb') as cache_file:
            cached_data = pickle.load(cache_file)

            if cached_data.version != CACHE_VERSION or \
                    cached_data.expired_at < datetime.now():
                log.info('cache expired or incompatible version, deleted')
                delete_cache()
                return None

            return cached_data

    except IOError:
        log.error('could not read cache file')
        return None
    except pickle.UnpicklingError:
        log.error('could not unpickle cached data')
        return None


def _load_or_new_cache() -> CachedData:
    cached_data = _load_cache()

    if cached_data:
        return cached_data

    return _new_cached_data()


def _store_cache(cached_data: CachedData) -> None:
    cache_dir = os.path.dirname(config.CACHE_PATH)

    if not os.access(cache_dir, os.F_TEST):
        os.makedirs(cache_dir)

    with open(config.CACHE_PATH, 'wb') as cache_file:
        pickle.dump(cached_data, cache_file, protocol=pickle.HIGHEST_PROTOCOL)


def save_problem_list(problem_list: List[Problem]) -> None:
    cached_data = _load_or_new_cache()

    cached_data.problem_list = problem_list
    cached_data.update_expire_time()

    _store_cache(cached_data)


def load_problem_list() -> Optional[List[Problem]]:
    cached_data = _load_or_new_cache()

    return cached_data.problem_list
