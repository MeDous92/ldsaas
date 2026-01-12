from datetime import datetime, timedelta, timezone

from models import User
from users.status import derive_status


def test_derive_status_pending():
    user = User(
        email="pending@example.com",
        status="pending",
        password_hash=None,
        invite_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        is_active=False,
    )
    assert derive_status(user) == "pending"


def test_derive_status_inactive():
    user = User(
        email="inactive@example.com",
        status="inactive",
        password_hash=None,
        invite_expires_at=None,
        is_active=False,
    )
    assert derive_status(user) == "inactive"


def test_derive_status_active():
    user = User(
        email="active@example.com",
        status="active",
        password_hash="hash",
        invite_expires_at=None,
        is_active=True,
    )
    assert derive_status(user) == "active"
