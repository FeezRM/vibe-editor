#!/usr/bin/env python3
"""Acquisition ladder rung 3 — capture a REAL interface as a still, headless, deterministic.

Uses the headless Chrome shell that hyperframes already installed (no new dependency).

Usage: python workflows/capture-url.py <url> <out.png> [--width 440] [--height 950] [--scale 2] [--wait 2500] [--full]
"""
import argparse
import glob
import os
import subprocess
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("url")
ap.add_argument("out")
ap.add_argument("--width", type=int, default=440)
ap.add_argument("--height", type=int, default=950)
ap.add_argument("--scale", type=float, default=2.0)
ap.add_argument("--wait", type=int, default=2500, help="ms to wait for the page before the shot")
ap.add_argument("--mobile", action="store_true", help="iPhone user agent")
a = ap.parse_args()

cands = sorted(glob.glob(os.path.expanduser("~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-mac-arm64/chrome-headless-shell"))) + \
        sorted(glob.glob(os.path.expanduser("~/.cache/puppeteer/chrome/*/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"))) + \
        ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] +         sorted(glob.glob(os.path.expanduser("~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-win64/chrome-headless-shell.exe"))) +         sorted(glob.glob(os.path.expanduser("~/.cache/puppeteer/chrome/*/chrome-win64/chrome.exe"))) +         [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]
chrome = next((c for c in cands if Path(c).exists()), None)
if not chrome:
    sys.exit("no headless chrome found — run `npx hyperframes doctor` once to install it")

out = Path(a.out).resolve()
out.parent.mkdir(parents=True, exist_ok=True)
cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox", "--disable-dev-shm-usage",
       f"--window-size={a.width},{a.height}", f"--force-device-scale-factor={a.scale}",
       f"--virtual-time-budget={a.wait}", f"--screenshot={out}"]
if a.mobile:
    cmd.append("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
cmd.append(a.url)
t0 = time.time()
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
if not out.exists():
    print(r.stderr[-1500:], file=sys.stderr)
    sys.exit(f"capture failed for {a.url}")
print(f"captured {a.url} → {out} ({a.width}x{a.height}@{a.scale}x, {time.time()-t0:.1f}s)")
