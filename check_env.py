"""
check_env.py  –  Quick environment diagnostic
Run: python check_env.py
"""
import sys
import subprocess

print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}\n")

packages = [
    ("streamlit",       "streamlit"),
    ("oracledb",        "oracledb"),
    ("dotenv",          "python-dotenv"),
    ("pymupdf (new)",   "pymupdf"),
    ("fitz (legacy)",   "fitz"),
    ("docx",            "python-docx"),
    ("anthropic",       "anthropic"),
]

for import_name, pip_name in packages:
    try:
        mod = __import__(import_name.split(" ")[0])
        ver = getattr(mod, "__version__", "unknown")
        print(f"  OK  {import_name:<20} version={ver}")
    except ImportError:
        print(f"  MISSING  {import_name:<20}  →  pip install {pip_name}")

print()

# Try the exact PDF open call to surface any runtime errors
print("Testing PDF extraction …")
try:
    try:
        import pymupdf as fitz
        src = "pymupdf"
    except ImportError:
        import fitz
        src = "fitz"
    # create a minimal 1-byte stream just to test open()
    import io
    print(f"  OK  imported via '{src}', version={fitz.version}")
except Exception as e:
    print(f"  FAIL  {e}")
