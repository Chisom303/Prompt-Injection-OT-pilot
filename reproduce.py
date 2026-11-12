#!/usr/bin/env python3
"""Reproduce every number in the paper's pilot tables from the published raw outputs.

    python reproduce.py

No GPU and no language model are needed; it takes about one minute.
Requirements: Python 3.10 or newer and numpy (matplotlib is optional and only draws the plots).

Steps:
  1. check that the bundled InjecAgent files and the published raw outputs are intact (SHA-256)
  2. recompute all statistics from the raw outputs          -> reproduced/summary.json, summary.csv
  3. rebuild Tables 5 and 6 (and the plots if matplotlib is installed) -> reproduced/tables.md
  4. recompute the sensitivity analysis and descriptive counts -> reproduced/sensitivity_fallback.json, descriptives.json
  5. compare every regenerated file with the published one in results/

Line endings are ignored in every check, so the result is the same on Windows, macOS and Linux.
The script ends with "REPRODUCTION PASSED" (exit status 0) or explains what differs.
"""
import hashlib, json, os, subprocess, sys

if sys.version_info < (3, 10):
    sys.exit(f"Python 3.10 or newer is needed (this is Python {sys.version.split()[0]}).")
try:
    import numpy  # noqa: F401
except ImportError:
    sys.exit("numpy is not installed. Run:  python -m pip install -r requirements.txt   and then run this script again.")

REPO = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.join(REPO, "pipeline")
RESULTS = os.path.join(REPO, "results")
RAW = [os.path.join(RESULTS, "raw", m) for m in ("llama3.1-8b-ctx8k", "qwen2.5-7b-ctx8k")]
OUT = os.path.join(REPO, "reproduced")
COMPARED = ["summary.json", "summary.csv", "tables.md", "sensitivity_fallback.json", "descriptives.json"]
BINARY = (".pdf", ".png", ".xlsx")
ENV = dict(os.environ, PYTHONUTF8="1")  # same text encoding on every operating system


def content(path):
    """File bytes with Windows line endings converted to Unix ones (binary files unchanged)."""
    with open(path, "rb") as f:
        data = f.read()
    return data if path.lower().endswith(BINARY) else data.replace(b"\r\n", b"\n")


def sha256(path):
    return hashlib.sha256(content(path)).hexdigest()


def check_sums(sums_file, base):
    bad = []
    with open(sums_file, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            digest, name = line.split(maxsplit=1)
            name = name.strip().lstrip("*")
            path = os.path.join(base, *name.split("/"))
            if not os.path.exists(path):
                bad.append(f"missing  {name}")
            elif sha256(path) != digest:
                bad.append(f"changed  {name}")
    return bad


def run(title, script, args):
    if title:
        print(title, flush=True)
    r = subprocess.run([sys.executable, os.path.join(PIPE, script)] + args, env=ENV,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        sys.exit(f"\n{script} failed:\n{r.stderr.strip()}")


def first_difference(a, b):
    la, lb = content(a).decode("utf-8").split("\n"), content(b).decode("utf-8").split("\n")
    for i, (x, y) in enumerate(zip(la, lb), 1):
        if x != y:
            return f"line {i}:\n      published:   {x[:150]}\n      regenerated: {y[:150]}"
    return f"different length ({len(la)} vs {len(lb)} lines)"


def headline():
    rows = json.load(open(os.path.join(OUT, "summary.json"), encoding="utf-8"))
    get = lambda m, v: next(r for r in rows if r["model"] == m and r["variant"] == v and r["subset"] == "all")
    print("\nKey results (Table 5 of the paper), attack success among valid outputs (%):")
    print(f"  {'':22}{'M0 none':>10}{'M1 tagging':>12}{'M3 least priv.':>16}")
    for m, name in (("llama3.1-8b-ctx8k", "Llama 3.1 8B"), ("qwen2.5-7b-ctx8k", "Qwen2.5 7B")):
        print(f"  {name:22}{get(m, 'none')['asr_valid']:>10}{get(m, 'm1')['asr_valid']:>12}{get(m, 'm3')['asr_valid']:>16}")


def main():
    print("1. Checking that the input files are intact", flush=True)
    bad = check_sums(os.path.join(REPO, "data", "injecagent", "SHA256SUMS"), os.path.join(REPO, "data", "injecagent"))
    bad += check_sums(os.path.join(RESULTS, "SHA256SUMS"), RESULTS)
    if bad:
        print("\n".join("   " + b for b in bad))
        sys.exit(f"\n{len(bad)} input file(s) are missing or changed, so the check cannot be trusted. "
                 "Download the repository again (as a zip or with git clone) and rerun.")
    print("   all input files match their published checksums")
    os.makedirs(OUT, exist_ok=True)
    run("2. Recomputing the statistics", "analyze.py", RAW + ["--out", OUT])
    run("3. Rebuilding the tables", "make_report.py", [os.path.join(OUT, "summary.json")])
    run("4. Recomputing the sensitivity analysis and descriptive counts", "sensitivity_fallback.py", RAW + ["--out", OUT])
    run("", "describe_outputs.py", RAW + ["--out", OUT])
    print("5. Comparing with the published results in results/")
    ok = True
    for name in COMPARED:
        a, b = os.path.join(RESULTS, name), os.path.join(OUT, name)
        same = content(a) == content(b)
        ok &= same
        print(f"   {'identical' if same else 'DIFFERENT'}  {name}")
        if not same:
            print("      first difference at " + first_difference(a, b))
    headline()
    if not ok:
        sys.exit("\nREPRODUCTION FAILED: the files marked DIFFERENT do not match. Please report the lines shown above.")
    print("\nREPRODUCTION PASSED: every reported value regenerates exactly from the raw outputs.")
    print(f"Regenerated files are in {OUT}")


if __name__ == "__main__":
    main()
