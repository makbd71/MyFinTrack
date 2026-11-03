# 03 — Generate & send reports

| Report | Runs (America/New_York) | Covers |
|---|---|---|
| Daily | every day 09:00 | previous day |
| Weekly | Sunday 20:00 | Monday–Sunday of that week |
| Monthly | last day of month 19:00 | whole month |

Command: `python -m execution.run_report --period daily|weekly|monthly`
Date ranges come from `execution/periods.py` (tested). The Excel button calls the same command.

Report content (lead with the bottom line): income, expense, net and change vs. previous period;
top 3 categories and merchants; spending per card; unusual items; unparsed emails to fix.
