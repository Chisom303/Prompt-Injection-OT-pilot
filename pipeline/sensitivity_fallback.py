#!/usr/bin/env python3
"""Sensitivity analysis: repeat the main comparisons after excluding every case in which a data-stealing
second step used a fallback simulated response (a cached response of the same tool, used when no cached
response matched the generated arguments). A case flagged under any condition is excluded from all conditions,
so the comparisons stay paired.

Usage: python sensitivity_fallback.py RAW_DIR [RAW_DIR ...] [--out OUT_DIR]
  writes OUT_DIR/sensitivity_fallback.json (default OUT_DIR: the parent of the first RAW_DIR)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze as A

COND = ["none", "m1", "m3", "m1m3"]


def run(model_dir):
    data, flagged = {}, set()
    for c in COND:
        rows = [json.loads(l) for s in ("base", "enhanced") for l in open(os.path.join(model_dir, f"{c}_{s}.jsonl"))]
        data[c] = rows
        flagged |= {(r["attack"], r["case_index"]) for r in rows if r.get("step2_fallback_response")}
    fallback_calls = [r for c in COND for r in data[c] if r.get("step2_fallback_response")]
    out = {"model": os.path.basename(model_dir.rstrip("/")), "flagged_cases": len(flagged),
           "fallback_calls": len(fallback_calls),
           "fallback_step2_outcomes": {o: sum(r.get("eval_step2") == o for r in fallback_calls) for o in ("succ", "unsucc", "invalid")},
           "conditions": {}}
    base = None
    for c in COND:
        kept = [A.case_fields(r) for r in data[c] if (r["attack"], r["case_index"]) not in flagged]
        full = A.metrics([A.case_fields(r) for r in data[c]], c in ("m3", "m1m3"))
        sub = A.metrics(kept, c in ("m3", "m1m3"))
        row = {"instances_kept": len(kept), "asr_valid_all": round(full["asr_valid"], 1), "asr_valid_excl": round(sub["asr_valid"], 1),
               "asr_all_all": round(full["asr_all"], 1), "asr_all_excl": round(sub["asr_all"], 1)}
        if c == "none":
            base = kept
        else:
            d, (lo, hi), p, k = A.cluster_compare(base, kept)
            row.update({"diff_vs_none_pp": round(d, 1), "diff_ci": [round(lo, 1), round(hi, 1)], "p_perm": round(p, 4), "clusters": k})
        out["conditions"][c] = row
    ps = sorted((v["p_perm"], k) for k, v in out["conditions"].items() if "p_perm" in v)
    running = 0.0
    for i, (p, k) in enumerate(ps):
        running = max(running, min(1.0, (len(ps) - i) * p))
        out["conditions"][k]["p_holm"] = round(running, 4)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Sensitivity analysis excluding fallback-response cases.")
    ap.add_argument("raw_dirs", nargs="+")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = [run(d) for d in a.raw_dirs]
    out_dir = a.out or os.path.dirname(os.path.abspath(a.raw_dirs[0]))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "sensitivity_fallback.json")
    json.dump(res, open(path, "w"), indent=1)
    print(json.dumps(res, indent=1))
