import threading

import pytest

from autoteam import api


class _FakeExecutor:
    def __init__(self, error):
        self.error = error

    def run(self, func, *args, **kwargs):
        raise self.error


def test_get_team_members_wraps_internal_error_as_json(monkeypatch):
    monkeypatch.setattr(api, "_playwright_lock", threading.Lock())
    monkeypatch.setattr(api, "_pw_executor", _FakeExecutor(RuntimeError("boom")))
    monkeypatch.setattr("autoteam.admin_state.get_admin_session_token", lambda: "session-abc")
    monkeypatch.setattr("autoteam.admin_state.get_chatgpt_account_id", lambda: "acc-123")

    with pytest.raises(api.HTTPException) as exc:
        api.get_team_members()

    assert exc.value.status_code == 400
    assert exc.value.detail == "boom"
    assert api._playwright_lock.locked() is False


def test_delete_account_wraps_internal_error_as_json(monkeypatch):
    monkeypatch.setattr(api, "_playwright_lock", threading.Lock())
    monkeypatch.setattr(api, "_pw_executor", _FakeExecutor(RuntimeError("boom")))
    monkeypatch.setattr(api, "_is_main_account_email", lambda email: False)
    monkeypatch.setattr("autoteam.accounts.load_accounts", lambda: [{"email": "target@example.com"}])

    with pytest.raises(api.HTTPException) as exc:
        api.delete_account("target@example.com")

    assert exc.value.status_code == 400
    assert exc.value.detail == "boom"
    assert api._playwright_lock.locked() is False
