# Tx Automation

> This project was created purely to showcase my creativity and technical approach. It does not have any other intended practical use, especially since the site's UI has likely changed after one or two years. At the time, backend access was also restricted, so this workflow could not be done through the backend. Thank you for your attention.

## About This Project

I built this project as a UI-based automation tool for repetitive wallet transaction workflows.  
It uses Python to automate browser actions, manage wallet progress in Excel, and keep track of transaction counts across multiple chains.

I originally made it as a personal challenge to see how far I could push desktop automation in a real workflow. The script is built around the exact UI coordinates that were valid at the time I wrote it, so it reflects the interface state from that period rather than a current production setup. [web:55][web:85]

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

After each wallet run, I save the updated transaction counters back into the spreadsheet so progress is never lost if the script stops unexpectedly. For a portfolio project, this kind of explanation is useful because it shows what the project does, what decisions I made, and what technical problem I solved. [web:85][web:87]

## Project Structure

```text
tx_automation/
├─ main.py
├─ config_loader.py
├─ config.json
├─ models.py
├─ wallet_selector.py
├─ telegram_logger.py
├─ ui_automation.py
├─ utils.py
├─ requirements.txt
├─ .env
├─ .env.example
├─ data/
│  └─ UnionTransactionChains2.xlsx
├─ logs/
│  ├─ app.log
│  └─ screenshots/
└─ README.md
```

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

## Hotkeys

- `F8` — Pause or resume the script.
- `ESC` — Stop the script safely.

## Logging

I save logs to:

```text
logs/app.log
```

I also support Telegram logging for important messages, but I keep it rate-limited so it does not spam. I prefer this because long-running automation jobs need clear visibility without overwhelming the notification channel. [web:80][web:86]

## Notes

This repository is intentionally kept as a snapshot of a workflow that made sense at the time I built it.  
It is not intended as a current production integration, and the UI assumptions may no longer match the live interface.

## Safety

- I never hardcode secrets in the source code.
- I keep Telegram credentials in `.env`.
- I avoid running the script while the mouse and keyboard are being used for something else.
- I understand that coordinate-based UI automation is sensitive to resolution, zoom, and layout changes.

## Disclaimer

This project is shared for portfolio and creativity purposes only.  
It reflects a historical UI workflow, not a guaranteed current automation path.
