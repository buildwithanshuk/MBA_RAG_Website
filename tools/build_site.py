"""
build_site.py
─────────────
Reads tools/notebook_meta.json, verifies each notebook file exists,
then injects a fresh NOTEBOOKS JavaScript array into index.html between
the markers:

    // NOTEBOOKS_START
    ...
    // NOTEBOOKS_END

Usage:
    python tools/build_site.py

Run this whenever you add a new notebook or update card metadata.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_FILE   = os.path.join(ROOT, "tools", "notebook_meta.json")
INDEX_FILE  = os.path.join(ROOT, "index.html")


def load_meta():
    with open(META_FILE, encoding="utf-8") as f:
        return json.load(f)


def verify_notebooks(meta):
    missing = []
    for nb in meta:
        path = os.path.join(ROOT, nb["file"])
        if not os.path.exists(path):
            missing.append(nb["file"])
    if missing:
        print("ERROR: The following notebook files are missing:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)
    print(f"✓  All {len(meta)} notebook files found.")


def build_js_array(meta):
    lines = ["const NOTEBOOKS = "]
    lines.append(json.dumps(meta, indent=2, ensure_ascii=False))
    lines.append(";")
    return "\n".join(lines)


def inject(js_array):
    with open(INDEX_FILE, encoding="utf-8") as f:
        html = f.read()

    pattern = r"(// NOTEBOOKS_START\n).*?(\n\s*// NOTEBOOKS_END)"
    replacement = r"\g<1>" + js_array + r"\2"

    new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)
    if count == 0:
        print("ERROR: Could not find // NOTEBOOKS_START … // NOTEBOOKS_END markers in index.html.")
        sys.exit(1)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"✓  Injected {len(json.loads(js_array.split(' = ', 1)[1].rstrip(';')))} notebook cards into index.html.")


def main():
    print("build_site.py — injecting notebook metadata into index.html\n")
    meta = load_meta()
    verify_notebooks(meta)
    js_array = build_js_array(meta)
    inject(js_array)
    print("\nDone. Refresh http://localhost:3000 to see changes.")


if __name__ == "__main__":
    main()
