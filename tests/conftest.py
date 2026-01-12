import os
import sys
import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


@pytest.fixture(scope="session")
def client():
    os.environ.setdefault("DATABASE_URL", "sqlite://")
    import db
    import main

    importlib.reload(db)
    importlib.reload(main)

    return TestClient(main.app)
