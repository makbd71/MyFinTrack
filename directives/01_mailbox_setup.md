# 01 — Mailbox setup & routing

**Goal:** a `FinComm` folder/label exists, and every financial sender is routed into it.

## Inputs
- `.env`: `MAIL_PROVIDER`, `MAIL_ADDRESS`, `MAIL_APP_PASSWORD`, `IMAP_HOST`, `FINCOMM_FOLDER`
- Gmail only: `credentials.json` (OAuth client) → creates `token_gmail.json` on first run

## Steps
1. Connect and create `FINCOMM_FOLDER` if missing (`execution/mailbox.py`). Must be idempotent.
2. Scan all folders except Trash and Spam. List distinct senders whose emails look financial
   (amounts, "transaction", "payment", "deposit", "card ending in" …).
3. Show the owner the candidate list **before** creating any rules. Add confirmed ones to `config/senders.yaml`.
4. Create server-side rules (`execution/rules.py`):
   - Gmail → Gmail API `users.settings.filters` (add label FinComm, skip inbox optional)
   - Outlook → Microsoft Graph `messageRules`
   - Other IMAP → Sieve if supported, else scheduled move script
5. Move existing matching emails into FinComm. **Never delete anything.**

## Edge cases / learnings
- Gmail "folders" are labels; IMAP CREATE makes a label.
- Gmail filters cannot be created over IMAP — OAuth is required.
