# AAB Pocket Task Board v0.1 (AAB-MVP-APP-001)

A small phone-friendly web app for recording programming goals (TODO / DOING / DONE) and exporting a JSON snapshot. Python 3.10+ standard library only; no accounts, no internet, no installs beyond Python.

## Run on Android (Termux, if Python is already present)
```
cd mvp_app_001
python3 app.py --port 8765
```
It prints `http://127.0.0.1:8765`. Open that address in the phone's browser. Optional: `--db path/to/goals.json` (default `goals.json` in the current folder).

## Short demo
1. Type "Build app" and tap **Add**.
2. Tap **DOING**, then **DONE** (tap **TODO** to move it back).
3. Tap **Export JSON** to download `pocket-task-board-export.json`.
4. Stop and restart the app: your goals are still there.

## Limitations
- Loopback only (127.0.0.1); no login, no remote access, not for production. Use fictitious tasks only.
- Local JSON file; no concurrency control or crash-safe database guarantees. A corrupt file is refused, never overwritten.
- No GitHub/Grok integration yet.

## STOP
Press **Ctrl+C** in Termux to shut the app down cleanly.
