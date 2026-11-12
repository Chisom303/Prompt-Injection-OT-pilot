#!/usr/bin/env python3
"""Quantify run-to-run variation between two independent runs of the pilot.

Usage: python compare_runs.py RUN1_MODEL_DIR RUN2_MODEL_DIR [more pairs ...]
  e.g. python pipeline/compare_runs.py results/raw/qwen2.5-7b-ctx8k outputs/qwen2.5-7b-ctx8k

For every condition and setting, the script matches instances by (attack family, case index) and reports:
  agreement on the scored outcome (success, failure or invalid), Cohen's kappa for attack success,
  and the attack success rate over all instances in each run with the difference in percentage points.
It writes run_variation.csv in the folder that contains the second directory.
"""
import csv, json, os, sys

COND = ["none", "m1", "m3", "m1m3"]
SETTINGS = ["base", "enhanced", "benign"]


def outcome(r):
    if r["attack"] == "ds" and r["eval"] == "succ":
        return "succ" if r.get("eval_step2") == "succ" else ("invalid" if r.get("eval_step2") == "invalid" else "unsucc")
    return r["eval"]


def load(path):
    if not os.path.exists(path):
        return {}
    return {(r["attack"], r["case_index"]): outcome(r) for r in map(json.loads, open(path))}


def kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def compare(d1, d2):
    rows = []
    for c in COND:
        for s in SETTINGS:
            r1, r2 = load(os.path.join(d1, f"{c}_{s}.jsonl")), load(os.path.join(d2, f"{c}_{s}.jsonl"))
            keys = sorted(r1.keys() & r2.keys())
            if not keys:
                continue
            o1, o2 = [r1[k] for k in keys], [r2[k] for k in keys]
            s1, s2 = [x == "succ" for x in o1], [x == "succ" for x in o2]
            rows.append({"model": os.path.basename(d1.rstrip("/")), "condition": c, "setting": s, "n": len(keys),
                         "outcome_agreement_pct": round(100 * sum(x == y for x, y in zip(o1, o2)) / len(keys), 1),
                         "kappa_success": round(kappa(s1, s2), 3),
                         "asr_all_run1_pct": round(100 * sum(s1) / len(keys), 1),
                         "asr_all_run2_pct": round(100 * sum(s2) / len(keys), 1),
                         "difference_pp": round(100 * (sum(s2) - sum(s1)) / len(keys), 1)})
    return rows


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2 or len(args) % 2:
        sys.exit(__doc__)
    rows = []
    for i in range(0, len(args), 2):
        rows += compare(args[i], args[i + 1])
    out = os.path.join(os.path.dirname(os.path.abspath(args[1])), "run_variation.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)
    print("wrote", out)
