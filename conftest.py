# Ensure repository root is on sys.path for absolute imports like `core.*`
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Optional: register custom markers to avoid warnings
import pytest  # type: ignore

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")


def pytest_ignore_collect(collection_path, config):  # type: ignore[no-redef]
    """Exclude auxiliary scripts and archives from collection.

    - testing_archive contains historical/manual tests not meant for pytest
    - tests/test_comparison.py is a script-style comparator (not a test function)
    """
    try:
        p = collection_path
        parts = set(p.parts)
        if "testing_archive" in parts:
            return True
        if ".venv" in parts or "site-packages" in parts:
            return True
        if p.name == "test_comparison.py":
            return True
    except Exception:
        pass
    return False
