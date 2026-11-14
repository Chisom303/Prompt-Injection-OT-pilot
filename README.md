# Indirect prompt injection in LLM agents for critical-infrastructure operations: pilot evaluation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24212460.svg)](https://doi.org/10.5281/zenodo.24212460)

Code, data and raw model outputs for the pilot evaluation in the paper
*Indirect prompt injection in LLM agents for critical-infrastructure operations: An attack-surface framework and exploratory benchmark study*.

Archived release: Alozie, C. (2026). *Chisom303/Prompt-Injection-OT-pilot: v1.0.0 - First release* (Version v1.0.0)
[Computer software]. Zenodo. https://doi.org/10.5281/zenodo.24212460. Citation metadata are in `CITATION.cff`.

The pilot measures three mitigations on a stratified sample of the InjecAgent benchmark with two open-weight models
(Llama 3.1 8B Instruct and Qwen2.5 7B Instruct): provenance tagging (M1), least privilege (M3) and a tool-name
allowlist gate (M2), against no defence (M0).

## Reproduce the results (about one minute, no GPU)

You need **Python 3.10 or newer**. Nothing else is downloaded: the benchmark data and all raw model outputs are in this repository.

**Option A: on your computer**

```bash
git clone https://github.com/Chisom303/Prompt-Injection-OT-pilot.git   # or download the ZIP and unzip it
cd Prompt-Injection-OT-pilot
python -m pip install -r requirements.txt
python reproduce.py
```

On some systems the command is `python3` instead of `python`. If you download the ZIP instead, the unzipped folder is named `Prompt-Injection-OT-pilot-main` (or after the release
tag); run the last two commands inside it. If you prefer an isolated environment, run
`python -m venv .venv`, activate it (`.venv\Scripts\activate` on Windows, `source .venv/bin/activate` elsewhere),
then the last two commands.

**Option B: in the browser, with nothing to install**

Open `notebooks/reproduce_in_colab.ipynb` in Google Colab (File, Open notebook, GitHub tab, paste this repository's
address) and choose Runtime, Run all.

**What you should see**

```
1. Checking that the input files are intact
   all input files match their published checksums
2. Recomputing the statistics
3. Rebuilding the tables
4. Recomputing the sensitivity analysis and descriptive counts
5. Comparing with the published results in results/
   identical  summary.json
   identical  summary.csv
   identical  tables.md
   identical  sensitivity_fallback.json
   identical  descriptives.json

Key results (Table 5 of the paper), attack success among valid outputs (%):
                           M0 none  M1 tagging  M3 least priv.
  Llama 3.1 8B                85.5        87.1             8.4
  Qwen2.5 7B                  40.5        31.1             0.9

REPRODUCTION PASSED: every reported value regenerates exactly from the raw outputs.
Regenerated files are in .../prompt-injection-ot-pilot/reproduced
```

`reproduce.py` recomputes every statistic, table and count in the paper from the raw model outputs, writes them to
`reproduced/`, and checks them against the published files in `results/`. Line endings are ignored, so the Windows
line-ending conversion done by Git or by unzipping tools does not affect the check. The published results regenerate identically with Python 3.10 to 3.13,
numpy 1.24 to 2.5 and matplotlib 3.7 to 3.11. matplotlib only draws the two plots; without it, every number is still
reproduced.

## Repository layout

```
reproduce.py              regenerate and verify every reported number from the raw outputs (start here)
run_experiment.py         optional: rerun the language models with Ollama (GPU, several hours)
pipeline/
  paths.py                repository paths shared by all scripts
  pilot.py                runs the agent on the sampled cases under M0, M1, M3 and M1+M3 and scores each output
  analyze.py              metrics, intervals, permutation tests, Holm adjustment, and the M2 gate
  make_report.py          Tables 5 and 6 (tables.md) and the two result plots
  sensitivity_fallback.py repeats the main comparisons without cases that used a fallback tool response
  describe_outputs.py     descriptive counts reported in Sections 6.1 and 6.6
  compare_runs.py         run-to-run variation between two independent runs
data/injecagent/          InjecAgent files used (commit f19c9f2, unmodified, MIT licence, with SHA256SUMS)
modelfiles/               Ollama Modelfiles that set the 8,192-token context window
notebooks/
  reproduce_in_colab.ipynb  run reproduce.py in the browser
  run_on_kaggle.ipynb     rerun the models on a free Kaggle GPU
results/                  published results (read-only)
  raw/<model>/            raw outputs: one JSON record per instance, plus sample_indices.json, run_info.json and
                          rerun_check.json (count of identical outputs in the 30-instance repeat; the repeat texts were not stored)
  summary.json, summary.csv, tables.md, sensitivity_fallback.json, descriptives.json, fig3_*.pdf/png, fig4_*.pdf/png
  SHA256SUMS              checksums of every file in results/
CITATION.cff              citation metadata for the archived release
docs/sample_overview.xlsx the 150 sampled cases and 100 benign cases, for inspection (not read by the code)
requirements.txt          packages for reproduce.py (numpy; matplotlib for the plots)
requirements-run.txt      packages for run_experiment.py
```

## Where each reported result comes from

| Paper | File in `results/` | Produced by |
| --- | --- | --- |
| Table 4, sample composition | `raw/<model>/sample_indices.json`, `docs/sample_overview.xlsx` | `pipeline/pilot.py` (stratified sample, seed 2026) |
| Table 5, pooled results | `tables.md` (Table 5), `summary.json` (subset `all`) | `pipeline/analyze.py`, `pipeline/make_report.py` |
| Table 6, results by setting and subset | `tables.md` (Table 6), `summary.json` | same |
| Fig. 3, attack success among valid outputs | `summary.json`; plot `fig3_attack_success.pdf` | same |
| Fig. 4, benign completion rate | `summary.json`; plot `fig4_benign_completion.pdf` | same |
| Section 6.1, invalid outputs, repeat check and outputs that reached the 512-token limit | `descriptives.json` (`output_cap`), `raw/<model>/rerun_check.json` | `pipeline/describe_outputs.py`, `pipeline/pilot.py` |
| Section 6.6, latency, tokens, fallback responses and sensitivity analysis | `summary.json`, `descriptives.json`, `sensitivity_fallback.json` | `pipeline/analyze.py`, `pipeline/describe_outputs.py`, `pipeline/sensitivity_fallback.py` |
| Section 5.4, models and environment | `raw/<model>/run_info.json` | `pipeline/pilot.py` |

In the paper, Figs. 3 and 4 are drawn as editable charts from `summary.json`; the PDF plots here show the same values.

Keys in `summary.json` and the corresponding terms in the paper:

| Key | Paper term |
| --- | --- |
| `valid` | Valid outputs (%) |
| `asr_valid` | Attack success rate among valid outputs |
| `asr_all` | Attack success rate over all instances |
| `osa` | Out-of-scope call rate |
| `executed` | Execution-eligible attack rate (calls the configuration would permit; nothing is executed against a backend) |
| `utility` | Benign completion rate (a proxy that does not check answer correctness) |
| `gate_false_block` | Benign cases blocked by the M2 gate (interventions consistent with its policy, not false positives) |
| `diff_asr_all_vs_none_pp`, `p_perm`, `p_holm` | Change in ASR over all instances relative to M0, permutation p-value, Holm-adjusted p-value |

Variants: `none` (M0), `m1` (M1), `m3` (M3), `m1m3` (M1+M3), and `none+M2`, `m1+M2`, `m1m3+M2` for the gate applied
after the fact to the stored outputs of those conditions.

## Rerun the models (optional)

The published run used Ollama 0.40.6 on NVIDIA Tesla T4 GPUs, 4-bit (Q4_K_M) models, temperature 0, seed 2026 and at
most 512 output tokens. A full run took about 4 hours for Qwen on a T4; Llama, whose outputs are longer, takes an estimated 7 hours.

```bash
python -m pip install -r requirements-run.txt
python run_experiment.py --check                 # 1-minute pipeline test with a mock model, no GPU needed
python run_experiment.py --models qwen2.5:7b     # one model; omit --models for both
```

New runs are written to `outputs/` and never touch `results/`. Interrupted runs resume where they stopped.
Generation was not fully reproducible even at temperature 0 (7 of 30 Llama and 6 of 30 Qwen repeat outputs matched
the original text exactly), so a rerun gives somewhat different rates. To measure the difference from the published run:

```bash
python pipeline/compare_runs.py results/raw/qwen2.5-7b-ctx8k outputs/qwen2.5-7b-ctx8k
```

This reports, for each condition and setting, the agreement of the scored outcomes, Cohen's kappa for attack success
and the change in attack success rate.

**On Kaggle (free GPU):** upload this folder as a dataset, open `notebooks/run_on_kaggle.ipynb`, add the dataset with
Add Input, set the accelerator to GPU T4 and internet on, choose the model in the first cell, and use
Save Version, Save & Run All. Download `outputs.zip` from the Output tab when the version finishes.

## Scope of the pilot

The pilot tests out-of-scope tool calls only: in every sampled case the attacker tools differ from the user tool, so
it says nothing about malicious arguments or harmful sequences using an authorized tool. The execution-eligible attack
rate measures permission to execute, not execution. M2 is a tool-name allowlist applied after the fact to stored
outputs, not a live gate and not a model of human approval. The benign completion rate does not check answer
correctness. The tools are InjecAgent's simulated consumer and office tools, not OT systems.

## Licence and attribution

Code in this repository: MIT licence (`LICENSE`). The files in `data/injecagent/` are from InjecAgent
(Zhan, Liang, Ying & Kang, 2024, Findings of ACL 2024, https://github.com/uiuc-kang-lab/InjecAgent) and remain under
their MIT licence (`data/injecagent/LICENCE`). Llama 3.1 and Qwen2.5 are used under their respective model licences
and are downloaded by Ollama, not redistributed here. If you use this material, please cite the paper.
