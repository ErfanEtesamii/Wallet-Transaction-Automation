# Tx Automation

> This project was created purely to showcase my creativity and technical approach. It does not have any other intended practical use, especially since the site's UI has likely changed after one or two years. At the time, backend access was also restricted, so this workflow could not be done through the backend. Thank you for your attention.

## About This Project

I built this project as a UI-based automation tool for repetitive wallet transaction workflows.
It uses Python to automate browser actions, manage wallet progress in Excel, and keep track of transaction counts across multiple chains.

I originally made it as a personal challenge to see how far I could push desktop automation in a real workflow. The script is built around the exact UI coordinates that were valid at the time I wrote it, so it reflects the interface state from that period rather than a current production setup.

## What I Built

I built a script that can:

- Switch between wallets in Keplr and Rabby.
- Fill transaction URLs and amounts automatically.
- Detect UI states with pixel checks.
- Retry fragile UI actions.
- Save wallet progress to Excel after each cycle.
- Resume from previously recorded transaction counts.
- Send optional Telegram logs for important events.

## How It Works

I read wallet records from an Excel file and select an incomplete wallet at random.
Then I switch to that wallet in the browser, open the relevant transfer flow, and automate the approval and confirmation steps using the original coordinates and color checks from my working version.

After each wallet run, I save the updated transaction counters back into the spreadsheet so progress is never lost if the script stops unexpectedly.

## Project Structure

```text
Wallet-Transaction-Automation/
├─ main.py                # Thin entry point
├─ src/
│  ├─ app.py               # TxAutomationApp - the automation loop
│  ├─ config_loader.py     # config.json + .env loading/validation
│  ├─ wallet_selector.py   # Excel-backed wallet queue
│  ├─ telegram_logger.py   # Rate-limited Telegram notifier
│  ├─ ui_automation.py     # pyautogui/pyperclip wrapper
│  └─ utils.py             # retry decorator, interruptible wait helper
├─ config.json
├─ requirements.txt
├─ .env / .env.example
├─ .gitignore
├─ data/                   # your wallets spreadsheet goes here
├─ logs/
│  ├─ app.log
│  └─ screenshots/
└─ README.md
```

All application code now lives under `src/`; `main.py` just wires it up and runs it. This is the only structural change - the automation logic and coordinate/UI flow are otherwise the same as before.

## Key Features

- I used the exact UI coordinates from my original working version.
- I centralized configuration in `config.json`.
- I moved secrets like Telegram credentials into `.env`.
- I added logging for observability.
- I added pause/resume with `F8`.
- I added stop control with `ESC`.
- I made the Excel update flow more resilient.
- I kept the design modular so it is easier to maintain later.

## Excel Format

My Excel file needs these columns:

| Column | Meaning |
|---|---|
| `name` | Wallet name |
| `HoleskyTransaction` | Current Holesky count |
| `BabylonTransaction` | Current Babylon count |
| `XionTransaction` | Current Xion count |
| `SeiTransaction` | Current Sei count |
| `Done` | `1` when the wallet is finished |

### Example

| name | HoleskyTransaction | BabylonTransaction | XionTransaction | SeiTransaction | Done |
|---|---:|---:|---:|---:|---:|
| wallet1 | 120 | 90 | 300 | 50 | 0 |
| wallet2 | 500 | 500 | 500 | 200 | 1 |

The app validates on startup that the sheet exists and has all of these columns, instead of failing partway through a run.

## Configuration

I use `config.json` for all non-secret settings and `.env` for sensitive values.

### `.env`

```env
TELEGRAM_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### `config.json`

This file contains:

- The Excel file path.
- Logging paths.
- Screenshot folder path.
- UI coordinates.
- Expected colors for pixel checks.
- Amount values.
- Target transaction limits.
- `auto_shutdown` - opt-in end-of-run shutdown prompt (off by default; see **Safety** below).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in TELEGRAM_TOKEN and TELEGRAM_CHAT_ID
python main.py
```

Put your wallets spreadsheet at the path set in `config.json` (`data/UnionTransactionChains2.xlsx` by default) before running.

## Hotkeys

- `F8` — Pause or resume the script.
- `ESC` — Stop the script safely.

If hotkey polling isn't available in your environment (e.g. no input-hook permission), the app logs a warning once and keeps running instead of crashing - ESC/F8 just won't work for that session.

## Logging

I save logs to:

```text
logs/app.log
```

I also support Telegram logging for important messages, but I keep it rate-limited so it does not spam.

## Notes

This repository is intentionally kept as a snapshot of a workflow that made sense at the time I built it.
It is not intended as a current production integration, and the UI assumptions may no longer match the live interface.

## Safety

- I never hardcode secrets in the source code.
- I keep Telegram credentials in `.env`, and `.env` is now git-ignored so it can't be committed by accident.
- I avoid running the script while the mouse and keyboard are being used for something else.
- I understand that coordinate-based UI automation is sensitive to resolution, zoom, and layout changes.
- The end-of-run shutdown/Chrome-kill prompt is **off by default**. Set `"auto_shutdown": true` in `config.json` if you want it; only enable it on a machine where an automatic shutdown and closing every Chrome window is actually what you want.

## Fixes in This Pass

A full review of the previous version turned up several bugs. All of the following are fixed:

1. **Xion transactions used the wrong configured amount.** `one_chain_xion` sent `amounts.sei` instead of `amounts.xion` from `config.json` - a copy-paste mismatch inconsistent with every other chain function, which each use their own amount. Xion transfers now use `amounts.xion` as intended.
2. **The wallet spreadsheet grew forever.** `WalletSelector.save()` reopened the file and *appended* a new "Last update" row on every single save - i.e. after every wallet processed. Left running, this silently added hundreds of junk rows over time. The timestamp is now written to one fixed, reserved cell instead of a new row each time.
3. **Telegram messages were silently dropped, not delayed.** If `send()` was called again before `telegram_min_interval_sec` had elapsed, the message was discarded with no error - so bursts of real events (several transactions succeeding close together) could vanish from the Telegram log. Messages are now queued and sent by a background thread as soon as the interval allows, so nothing is lost and the automation loop is never blocked waiting on the network.
4. **A page that failed to load could hang the script forever.** `prepare_transaction()` ended in an unbounded `while True` loop waiting for a button pixel that might never appear (bad page load, wrong window focus, a captcha). It now waits up to a configurable timeout and reports failure so the caller retries it like any other failed attempt, instead of freezing with no log line and no way to recover short of killing the process.
5. **One bad hotkey check could crash the whole run.** `keyboard.is_pressed()` can raise if the OS/session doesn't allow the input hook. That exception is now caught; ESC/F8 are disabled for the rest of that run (logged once) instead of the automation crashing outright.
6. **The end-of-run routine shut down the whole PC by default.** Unless you actively typed "No" within 20 seconds, the script force-killed every Chrome process and shut the machine down - every time it finished. This is now opt-in via `auto_shutdown` in `config.json` (default `false`), and only runs on Windows, where the underlying commands are even valid.
7. **Dead/unused code removed:** an unused `models.py` whose field names (`holesky`, `babylon`, ...) didn't match the dict keys (`HoleskyTransaction`, ...) actually used everywhere else, and an unused `wait_and_click_approve()` helper in `ui_automation.py` that duplicated logic already inlined in the main transaction loop.
8. **Dead dependency removed:** `pandas` was listed in `requirements.txt` but never imported anywhere; the code only uses `openpyxl` directly.
9. **No `.gitignore` and no `.env.example`**, despite the README describing both. `.env` is now git-ignored (it previously had no protection against being committed with real credentials filled in), and `.env.example` is included.
10. **Minor robustness:** startup now fails fast with a clear error if the wallet spreadsheet is missing or missing a required column, instead of failing deep inside a run; `update_wallet`/`mark_wallet_done` now raise if a wallet name isn't found instead of silently doing nothing; the "N consecutive failed transactions" log line now reports the actual configured `max_fail_streak` instead of a hardcoded `10`.

## Disclaimer

This project is shared for portfolio and creativity purposes only.
It reflects a historical UI workflow, not a guaranteed current automation path.
