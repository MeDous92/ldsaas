from auth.service import _hash_invite_token, _verify_invite_token


def test_invite_token_hash_verify():
    raw = "raw-token-123"
    hashed = _hash_invite_token(raw)
    assert _verify_invite_token(raw, hashed) is True
    assert _verify_invite_token("wrong-token", hashed) is False
