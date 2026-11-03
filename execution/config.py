"""Load settings from .env. The only place that reads environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def _bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    mail_provider: str
    mail_address: str
    mail_app_password: str
    imap_host: str
    imap_port: int
    smtp_host: str
    smtp_port: int
    fincomm_folder: str
    gmail_oauth_client_file: Path
    gmail_oauth_token_file: Path
    report_recipient: str
    timezone: ZoneInfo
    base_currency: str
    gsheets_enabled: bool
    google_account: str
    google_oauth_token_file: Path
    google_sheet_id: str
    db_path: Path
    output_dir: Path
    log_dir: Path

    def __repr__(self) -> str:  # never print secrets
        return f"Settings(mail_address={self.mail_address!r}, provider={self.mail_provider!r}, tz={self.timezone})"


def _path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def load_settings(env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or ROOT / ".env", override=False)
    g = os.getenv
    return Settings(
        mail_provider=g("MAIL_PROVIDER", "gmail"),
        mail_address=g("MAIL_ADDRESS", ""),
        mail_app_password=g("MAIL_APP_PASSWORD", ""),
        imap_host=g("IMAP_HOST", "imap.gmail.com"),
        imap_port=int(g("IMAP_PORT", "993")),
        smtp_host=g("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(g("SMTP_PORT", "587")),
        fincomm_folder=g("FINCOMM_FOLDER", "FinComm"),
        gmail_oauth_client_file=_path(g("GMAIL_OAUTH_CLIENT_FILE", "credentials.json")),
        gmail_oauth_token_file=_path(g("GMAIL_OAUTH_TOKEN_FILE", "token_gmail.json")),
        report_recipient=g("REPORT_RECIPIENT", ""),
        timezone=ZoneInfo(g("TIMEZONE", "America/New_York")),
        base_currency=g("BASE_CURRENCY", "USD"),
        gsheets_enabled=_bool(g("GSHEETS_ENABLED")),
        google_account=g("GOOGLE_ACCOUNT", ""),
        google_oauth_token_file=_path(g("GOOGLE_OAUTH_TOKEN_FILE", "token_gsheets.json")),
        google_sheet_id=g("GOOGLE_SHEET_ID", ""),
        db_path=_path(g("DB_PATH", "data/fincomm.db")),
        output_dir=_path(g("OUTPUT_DIR", "output")),
        log_dir=_path(g("LOG_DIR", "logs")),
    )
