from zoneinfo import ZoneInfo

from execution.config import load_settings


def test_example_env_loads(tmp_path, monkeypatch):
    for k in ["TIMEZONE", "BASE_CURRENCY", "GSHEETS_ENABLED", "MAIL_APP_PASSWORD"]:
        monkeypatch.delenv(k, raising=False)
    env = tmp_path / ".env"
    env.write_text("TIMEZONE=America/New_York\nBASE_CURRENCY=USD\nMAIL_APP_PASSWORD=secret\n")
    s = load_settings(env)
    assert s.timezone == ZoneInfo("America/New_York")
    assert s.base_currency == "USD"
    assert s.gsheets_enabled is False
    assert "secret" not in repr(s)
