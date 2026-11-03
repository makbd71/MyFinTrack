# MyFinTrack (FinComm)

Reads your financial emails, sorts them into a `FinComm` folder, and sends you
daily, weekly and monthly income/expense reports in Excel. Instructions for the
AI agent are in [CLAUDE.md](CLAUDE.md).

## Setup
```bash
./setup.sh
```
Then edit `.env`:
- `MAIL_ADDRESS`: your email address
- `MAIL_APP_PASSWORD`: a Gmail **app password** (Google Account → Security → 2-Step Verification → App passwords), not your normal password
- `REPORT_RECIPIENT`: where reports are sent

Run tests any time: `.venv/bin/python -m pytest`

## Status
- [x] Project structure, settings, transaction model, database, report date ranges (tested)
- [ ] Mailbox connection and FinComm folder
- [ ] Sender discovery and routing rules
- [ ] Per-sender parsers
- [ ] Excel workbook and Generate Report button
- [ ] Scheduled reports and email delivery
- [ ] Optional Google Sheets
