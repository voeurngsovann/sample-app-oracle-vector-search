"""
diag.py  –  Environment diagnostic
Runs automatically before Streamlit starts (see run.bat).
Writes diag.log in the project folder.
"""
import sys
import os
import traceback
import importlib
import datetime

LOG = os.path.join(os.path.dirname(__file__), "diag.log")

lines = []

def log(msg=""):
    lines.append(msg)
    print(msg)

log(f"=== Diagnostic  {datetime.datetime.now()} ===")
log()

# 1. Python identity
log(f"python exe  : {sys.executable}")
log(f"python ver  : {sys.version}")
log()

# 2. sys.path  (where imports are resolved from)
log("sys.path entries:")
for p in sys.path:
    log(f"  {p}")
log()

# 3. venv sanity — are we inside the project venv?
venv_expected = os.path.join(os.path.dirname(__file__), ".venv")
in_venv = sys.executable.startswith(venv_expected)
log(f"inside project venv : {'YES' if in_venv else 'NO  <-- problem here'}")
log()

# 4. Try every known pymupdf import path and report exact failure
for name in ("pymupdf", "fitz"):
    try:
        mod = importlib.import_module(name)
        log(f"import {name:<10} OK   version={mod.__version__}  file={mod.__file__}")
    except Exception:
        log(f"import {name:<10} FAIL")
        for ln in traceback.format_exc().splitlines():
            log(f"  {ln}")
log()

# 5. pip list — what is actually installed in this Python
log("installed packages (pip list):")
try:
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=columns"],
        capture_output=True, text=True
    )
    for ln in result.stdout.splitlines():
        log(f"  {ln}")
except Exception:
    log("  could not run pip list")

log()
log("=== end ===")

with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\nLog written to: {LOG}\n")
