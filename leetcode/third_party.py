import os.path
import sys

third_party_path = os.path.join(os.path.dirname(__file__), '../third_party')
sys.path.append(third_party_path)

# pylint: disable=C0413
import requests

if sys.version_info.minor == 6:
    # Python 3.6 does not support dataclass
    py36_extra_path = os.path.join(third_party_path, '3.6-only')
    sys.path.append(py36_extra_path)

# For Python 3.7 and above, use the standard library
# pylint: disable=C0411
from dataclasses import dataclass


__all__ = ('requests', 'dataclass')
