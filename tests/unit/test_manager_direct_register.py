from autoteam import manager


class _FakeMailClient:
    def create_temp_email(self):
        return "cloud-1", "direct@example.com"

    def delete_account(self, _account_id):
        raise AssertionError("delete_account should not be called")


class _FakeExecutor:
    def __init__(self):
        self.calls = []

    def run(self, func, *args, **kwargs):
        self.calls.append((func, args, kwargs))
        return func(*args, **kwargs)


def test_create_account_direct_dispatches_direct_register_via_browser_executor(monkeypatch):
    mail_client = _FakeMailClient()
    executor = _FakeExecutor()
    direct_calls = []

    monkeypatch.setattr(manager, "_browser_executor", executor)
    monkeypatch.setattr(
        manager,
        "_run_direct_register_once",
        lambda *args, **kwargs: direct_calls.append((args, kwargs)) or True,
    )
    monkeypatch.setattr(manager, "_is_email_in_team", lambda email: email == "direct@example.com")
    monkeypatch.setattr(manager, "add_account", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        manager,
        "_login_codex_with_result",
        lambda *args, **kwargs: {"ok": True, "bundle": {"plan_type": "team"}},
    )
    monkeypatch.setattr(manager, "save_auth_file", lambda bundle: "auth-file.json")
    monkeypatch.setattr(manager, "update_account", lambda *args, **kwargs: None)
    monkeypatch.setattr(manager, "_auth_repair_reset", lambda email: None)
    monkeypatch.setattr(manager, "STATUS_ACTIVE", "active")

    result = manager.create_account_direct(mail_client)

    assert result == "direct@example.com"
    assert len(executor.calls) == 1
    func, args, kwargs = executor.calls[0]
    assert func is manager._run_direct_register_once
    assert args == (mail_client, "direct@example.com", args[2])
    assert kwargs == {"mail_account_id": "cloud-1"}
    assert direct_calls == [((mail_client, "direct@example.com", args[2]), {"mail_account_id": "cloud-1"})]
