# AAB Doctor v0.1 (Android / Termux only)

**Status:** prototype awaiting ChatGPT independent review. Do **not** run it until the reviewer and the owner say so.

## What it does
Checks your phone's programming setup in one go and prints a report. It only *looks*: it installs nothing, changes nothing, writes no files, uses no internet and never asks for passwords.

It checks: the phone system type, whether you are inside Termux, the Python version, and whether `git`, `gh` and `codex` are present (by asking each one for its version number). It cannot read Android battery or settings, so those are always marked UNVERIFIED.

## The one command
In the Termux app, in the folder that holds `doctor.py`, type:

```
python3 doctor.py
```

(Reviewers may use `python3 doctor.py --json` for the machine-readable report.)

## Expected output (example, fictional)
```
AAB Doctor (aab-doctor/0.1) overall: UNVERIFIED
  [PASS] platform - Linux; Termux indicator present
  [PASS] python - Python 3.12.1
  [PASS] tool:git - git version 2.47.0
  [UNVERIFIED] tool:gh - gh not found on PATH
  [PASS] tool:codex - codex-cli 0.40.0
  [UNVERIFIED] android_settings - Battery optimisation and Android settings cannot be read by this tool
Next: Install gh in Termux - separate owner action
STOP. Do not run anything else.
```
Each line is PASS, FAIL or UNVERIFIED. UNVERIFIED for Android settings is normal.

If you see `python3: command not found`, Python is missing; the tool cannot run. Report that and stop.

## STOP
After the report appears, **STOP**. Do not follow the "Next" suggestion yourself, do not install anything and do not paste the output anywhere public. Send the report to the reviewer through the agreed route only.
