from mailer import build_invite_email


def test_build_invite_email_uses_explicit_url():
    msg = build_invite_email(
        to="user@example.com",
        token="token123",
        name="Test User",
        invite_url="https://example.com/accept?token=token123",
    )

    assert "invited to L&D SaaS" in msg["Subject"]
    assert msg["To"] == "user@example.com"
    body = msg.get_body(preferencelist=("html", "plain")).get_content()
    assert "https://example.com/accept?token=token123" in body
