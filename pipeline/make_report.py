#!/usr/bin/env python3
"""Turn results/summary.json (from analyze.py) into manuscript tables and figures.

Outputs (next to summary.json):
  tables.md   Table 5 (pooled results per model and condition) and Table 6 (by setting and subset)
  fig3_attack_success.pdf/.png   attack success among valid outputs, all cases vs actuation subset, 95% CI
  fig4_benign_completion.pdf/.png      benign completion rate per condition and model, 95% CI
Usage: python make_report.py OUT_DIR/summary.json
Nothing here is typed by hand: every value comes from summary.json.
"""
import json, os, sys
try:  # plots are optional: the tables do not need matplotlib
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

ORDER = ["none", "m1", "m3", "m1m3", "none+M2", "m1+M2", "m1m3+M2"]
LABEL = {"none": "M0 none", "m1": "M1 tagging", "m3": "M3 least privilege", "m1m3": "M1+M3",
         "none+M2": "M0+M2 gate", "m1+M2": "M1+M2", "m1m3+M2": "M1+M3+M2"}
SHORT = {"none": "M0", "m1": "M1", "m3": "M3", "m1m3": "M1+M3", "none+M2": "M0+M2", "m1+M2": "M1+M2", "m1m3+M2": "M1+M3+M2"}
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
BLUE, ORANGE = "#2a78d6", "#eb6834"  # validated categorical slots 1 and 2 (light mode)


def ci(r, k):
    return r.get(k + "_ci", "")


def table5(rows, models):
    out = ["Table 5. Pilot results pooled over base and enhanced settings (300 attack instances and 100 benign instances per condition and model). "
           "Values are percentages with 95% case-level cluster-bootstrap confidence intervals (10,000 resamples); Wilson intervals where every observed outcome is identical. "
           "Execution-eligible attacks are zero by design under M3 and the M2 allowlist gate. "
           "p (Holm): case-level permutation test of attack success over all instances against M0, Holm-adjusted within each model.", ""]
    out.append("| Model | Condition | Valid | ASR among valid (attempted) | Out-of-scope call | Execution-eligible attacks | Benign completion | Benign gate interventions | Diff. in ASR over all vs M0 (pp) | p (Holm) |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for m in models:
        for v in ORDER:
            r = next((x for x in rows if x["model"] == m and x["variant"] == v and x["subset"] == "all"), None)
            if not r:
                continue
            out.append(f"| {m} | {LABEL[v]} | {r['valid']:.1f} | {r['asr_valid']:.1f} {ci(r,'asr_valid')} | {r['osa']:.1f} {ci(r,'osa')} | "
                       f"{'0.0 (by design)' if (v in ('m3', 'm1m3') or v.endswith('+M2')) else str(r['executed']) + ' ' + ci(r,'executed')} | {'n.m. (post hoc gate)' if 'M2' in v else str(r.get('utility','')) + ' ' + r.get('utility_ci','')} | {r.get('gate_false_block','n/a') if 'M2' in v else 'n/a'} | {str(r['diff_asr_all_vs_none_pp']) + ' ' + r['diff_asr_all_vs_none_ci'] if 'diff_asr_all_vs_none_pp' in r else ''} | {('< 0.001' if r['p_holm'] < 0.001 else round(r['p_holm'], 3)) if 'p_holm' in r else ('ref.' if v=='none' else '')} |")
    return "\n".join(out)


def table6(rows, models):
    out = ["Table 6. Attack success among valid outputs (attempted) by attack setting and subset, in percent with 95% cluster-bootstrap confidence intervals (Wilson where every observed outcome is identical). "
           "Base and enhanced: 150 instances each. Physical harm: 120 instances. Actuation: 72 instances (traffic control, smart locks, home devices, indoor robot).", ""]
    out.append("| Model | Condition | Base | Enhanced | Physical harm | Actuation |")
    out.append("| --- | --- | --- | --- | --- | --- |")
    for m in models:
        for v in ["none", "m1", "m3", "m1m3"]:
            cells = []
            for s in ["base", "enhanced", "physical-harm", "actuation"]:
                r = next((x for x in rows if x["model"] == m and x["variant"] == v and x["subset"] == s), None)
                cells.append(f"{r['asr_valid']:.1f} {ci(r,'asr_valid')}" if r else "")
            out.append(f"| {m} | {LABEL[v]} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=8, length=3)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def parse_ci(s):
    lo, hi = s.strip("[]").split(",")
    return float(lo), float(hi)


def fig2(rows, models, out, mock):
    conds = ["none", "m1", "m3", "m1m3"]
    fig, axes = plt.subplots(1, len(models), figsize=(3.4 * len(models), 3.0), sharey=True, squeeze=False)
    for ax, m in zip(axes[0], models):
        style(ax)
        for j, (subset, color, marker, dx, name) in enumerate([("all", BLUE, "o", -0.12, "All cases"), ("actuation", ORANGE, "s", 0.12, "Actuation subset")]):
            xs, ys, err = [], [], [[], []]
            for i, v in enumerate(conds):
                r = next((x for x in rows if x["model"] == m and x["variant"] == v and x["subset"] == subset), None)
                if not r:
                    continue
                lo, hi = parse_ci(r["asr_valid_ci"])
                xs.append(i + dx); ys.append(r["asr_valid"]); err[0].append(r["asr_valid"] - lo); err[1].append(hi - r["asr_valid"])
            ax.errorbar(xs, ys, yerr=err, fmt=marker, color=color, ecolor=color, elinewidth=1.2, capsize=3, markersize=6,
                        markeredgecolor=SURFACE, markeredgewidth=1, label=name)
        ax.set_xticks(range(len(conds)))
        ax.set_xticklabels([SHORT[c] for c in conds], color=INK)
        ax.set_title(m, fontsize=9, color=INK, loc="left")
        ax.set_ylim(0, 100)
    axes[0][0].set_ylabel("Attack success among valid outputs (%)", fontsize=8, color=INK)
    axes[0][0].legend(frameon=False, fontsize=8, loc="upper right")
    if mock:
        fig.text(0.5, 0.5, "MOCK DATA - NOT RESULTS", ha="center", va="center", fontsize=22, color="#c00000", alpha=0.35, rotation=20)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}/fig3_attack_success.{ext}", dpi=300)
    plt.close(fig)


def fig3(rows, models, out, mock):
    """Benign completion rate per model-level condition with 95% CI; models told apart by marker and shade."""
    conds = ["none", "m1", "m3", "m1m3"]
    shades = [INK, MUTED, "#8a8985", "#b5b4af"]
    markers = ["o", "s", "^", "D"]
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    style(ax)
    width = 0.5 / max(1, len(models))
    for k, m in enumerate(models):
        xs, ys, err = [], [], [[], []]
        for i, v in enumerate(conds):
            r = next((x for x in rows if x["model"] == m and x["variant"] == v and x["subset"] == "all"), None)
            if not r or "utility" not in r:
                continue
            lo, hi = parse_ci(r["utility_ci"])
            xs.append(i - 0.25 + width / 2 + k * width); ys.append(r["utility"])
            err[0].append(r["utility"] - lo); err[1].append(hi - r["utility"])
        ax.errorbar(xs, ys, yerr=err, fmt=markers[k % 4], color=shades[k % 4], ecolor=shades[k % 4], elinewidth=1.2,
                    capsize=3, markersize=6, markeredgecolor=SURFACE, markeredgewidth=1, label=m)
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([SHORT[c] for c in conds], color=INK)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Benign completion rate (%)", fontsize=8, color=INK)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    if mock:
        fig.text(0.5, 0.5, "MOCK DATA - NOT RESULTS", ha="center", va="center", fontsize=16, color="#c00000", alpha=0.35, rotation=20)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{out}/fig4_benign_completion.{ext}", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    path = sys.argv[1]
    rows = json.load(open(path))
    out = os.path.dirname(os.path.abspath(path))
    models = list(dict.fromkeys(r["model"] for r in rows))
    mock = any(m.upper() == "MOCK" for m in models)
    with open(os.path.join(out, "tables.md"), "w") as f:
        if mock:
            f.write("MOCK DATA - NOT RESULTS\n\n")
        f.write(table5(rows, models) + "\n\n" + table6(rows, models) + "\n")
    if plt is None:
        print(f"wrote tables.md to {out} (matplotlib not installed, so the plots were skipped)")
    else:
        fig2(rows, models, out, mock)
        fig3(rows, models, out, mock)
        print(f"wrote tables.md, fig3_attack_success.pdf/png, fig4_benign_completion.pdf/png to {out}")
