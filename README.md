# ChSShKracker (Python)

Modular Python port of the provided Go SSH brute-force and honeypot-detection tool.

## Quick start

1. Create and activate a virtual environment (recommended).
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python run.py`

## Project structure

```
chsshkracker/
  __init__.py
  cli.py
  config.py
  models.py
  utils/
    __init__.py
    files.py
    logging_utils.py
    time_utils.py
  ssh/
    __init__.py
    client.py
    commands.py
    system_info.py
  detection/
    __init__.py
    honeypot.py
  workers/
    __init__.py
    pool.py
```

## Notes

- Functionality mirrors the original Go code: combo generation, worker pool with per-worker concurrency, system info gathering, honeypot scoring, and live banner.
- Outputs `su-goods.txt`, `detailed-results.txt`, and `honeypots.txt` in the working directory.
