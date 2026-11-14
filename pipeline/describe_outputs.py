#!/usr/bin/env python3
"""Descriptive counts reported in Sections 6.1 and 6.6 of the paper, computed from the raw outputs.

For each model:
  invalid_m0               attack instances under M0 (base and enhanced) with an invalid first or second step
  invalid_m0_recall        of these, instances whose invalid reason is a repeated call of the user tool
                           (InjecAgent reasons beginning "Recalling ...")
  invalid_reasons_m0       all invalid reasons under M0 with their counts
  max_prompt_tokens        longest prompt per condition (attack instances)
  second_step_calls        data-stealing second steps across M0, M1, M3 and M1+M3
  fallback_calls / fallback_cases   second steps that used a fallback cached tool response, and the cases involved
  rerun_check              the repeat of the first 30 M0 base instances (identical output text); only the count of
                           identical outputs was stored during the run, not the repeated output texts
  output_cap               first-step outputs that reached the 512-token output limit, per condition: attack
                           instances, how many of them were scored invalid, how many contain an Action line (so the
                           scored first action was emitted before the limit), and benign instances, how many of them
                           lack a final answer (and therefore count as not completed)

Usage: python describe_outputs.py RAW_DIR [RAW_DIR ...] [--out OUT_DIR]   (writes OUT_DIR/descriptives.json)
"""
import argparse, collections, json, os, re

COND = ["none", "m1", "m3", "m1m3"]
MAX_TOKENS = 512  # output limit used in the published run (see run_info.json)


def rows(model_dir, cond, settings=("base", "enhanced")):
    return [json.loads(l) for s in settings for l in open(os.path.join(model_dir, f"{cond}_{s}.jsonl"))]


def at_cap(r):
    return ((r.get("usage") or {}).get("completion_tokens") or 0) >= MAX_TOKENS


def output_cap(model_dir):
    res = {}
    for c in COND:
        att = [r for r in rows(model_dir, c) if at_cap(r)]
        ben = [r for r in rows(model_dir, c, ("benign",)) if at_cap(r)]
        res[c] = {"attack_instances": len(att),
                  "attack_invalid": sum(r["eval"] == "invalid" for r in att),
                  "attack_with_action_line": sum(bool(re.search(r"Action\s*:", r.get("output") or "")) for r in att),
                  "benign_instances": len(ben),
                  "benign_without_final_answer": sum("Final Answer:" not in (r.get("output") or "") for r in ben)}
    return res


def describe(model_dir):
    m0 = rows(model_dir, "none")
    reasons = collections.Counter()
    for r in m0:
        if r["eval"] == "invalid":
            reasons[r.get("invalid_reason")] += 1
        elif r.get("eval_step2") == "invalid":
            reasons[r.get("invalid_reason_step2")] += 1
    allc = {c: rows(model_dir, c) for c in COND}
    step2 = [r for c in COND for r in allc[c] if "output_step2" in r]
    fb = [r for r in step2 if r.get("step2_fallback_response")]
    return {
        "model": os.path.basename(os.path.abspath(model_dir)),
        "invalid_m0": sum(reasons.values()),
        "invalid_m0_recall": sum(v for k, v in reasons.items() if str(k).startswith("Recalling")),
        "invalid_reasons_m0": dict(reasons.most_common()),
        "max_prompt_tokens": {c: max((r.get("usage") or {}).get("prompt_tokens") or 0 for r in allc[c]) for c in COND},
        "second_step_calls": len(step2),
        "fallback_calls": len(fb),
        "fallback_cases": len({(r["attack"], r["case_index"]) for r in fb}),
        "rerun_check": json.load(open(os.path.join(model_dir, "rerun_check.json"))),
        "output_cap": output_cap(model_dir),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Descriptive counts from the raw outputs.")
    ap.add_argument("raw_dirs", nargs="+")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = [describe(d) for d in a.raw_dirs]
    out_dir = a.out or os.path.dirname(os.path.abspath(a.raw_dirs[0]))
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, "descriptives.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
