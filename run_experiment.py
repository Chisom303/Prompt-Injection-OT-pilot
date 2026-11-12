#!/usr/bin/env python3
"""Rerun the pilot with the language models (GPU recommended; about 4 to 7 hours per model on a T4).

  python run_experiment.py --check                     # 1-minute pipeline test with a mock model, no GPU
  python run_experiment.py                             # both models, all conditions
  python run_experiment.py --models qwen2.5:7b         # one model
  python run_experiment.py --out outputs/rep1          # write an independent replication to its own folder

What it does:
  1. checks that Ollama is installed and starts the server if needed
  2. downloads llama3.1:8b and qwen2.5:7b if missing (about 5 GB each)
  3. builds the 8,192-token-context models from modelfiles/ (a shorter window would silently truncate prompts)
  4. runs every condition for each model with pipeline/pilot.py (resumes automatically if interrupted)
  5. computes the statistics, tables, plots, sensitivity analysis and descriptive counts in the output folder

New runs never touch results/, which holds the published outputs.
Generation is not fully reproducible even at temperature 0, so a rerun gives somewhat different rates;
use pipeline/compare_runs.py to measure the difference from the published run.
"""
import argparse, os, shutil, subprocess, sys, time, urllib.request

REPO = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.join(REPO, "pipeline")
MODELFILES = os.path.join(REPO, "modelfiles")
MODELS = {"llama3.1:8b": "llama3.1-8b-ctx8k", "qwen2.5:7b": "qwen2.5-7b-ctx8k"}


ENV = dict(os.environ, PYTHONUTF8="1")  # same text encoding on every operating system


def sh(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env=ENV)


def ollama_up(url="http://localhost:11434/api/version"):
    try:
        urllib.request.urlopen(url, timeout=5)
        return True
    except Exception:
        return False


def finish(py, out, dirs, mock=False):
    sh([py, os.path.join(PIPE, "analyze.py")] + dirs + ["--out", out])
    sh([py, os.path.join(PIPE, "make_report.py"), os.path.join(out, "summary.json")])
    if not mock:
        sh([py, os.path.join(PIPE, "sensitivity_fallback.py")] + dirs + ["--out", out])
        sh([py, os.path.join(PIPE, "describe_outputs.py")] + dirs + ["--out", out])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="pipeline test with a mock model (numbers are meaningless)")
    ap.add_argument("--models", default=",".join(MODELS), help="comma-separated Ollama base models")
    ap.add_argument("--out", default=os.path.join(REPO, "outputs"), help="output folder (default: outputs/)")
    args = ap.parse_args()
    py = sys.executable
    out = os.path.abspath(args.out)
    try:
        inside_results = os.path.commonpath([out, os.path.join(REPO, "results")]) == os.path.join(REPO, "results")
    except ValueError:  # different drives on Windows
        inside_results = False
    if inside_results:
        sys.exit("Refusing to write into results/, which holds the published outputs. Choose another --out.")

    if args.check:
        out = os.path.join(out, "check")
        shutil.rmtree(out, ignore_errors=True)
        sh([py, os.path.join(PIPE, "pilot.py"), "--model", "MOCK", "--mock", "--out", out, "--rerun-check", "5"])
        finish(py, out, [os.path.join(out, "MOCK")], mock=True)
        print(f"\nPipeline OK ({out}). Mock numbers are random; never report them.")
        return

    if not shutil.which("ollama"):
        sys.exit("Ollama is not installed. Install it from https://ollama.com/download, then run this again.")
    if not ollama_up():
        print("Starting the Ollama server ...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            time.sleep(1)
            if ollama_up():
                break
        else:
            sys.exit("Could not start Ollama. Run 'ollama serve' in another window and retry.")

    dirs = []
    for base in args.models.split(","):
        if base not in MODELS:
            sys.exit(f"Unknown model {base}; the paper uses: {', '.join(MODELS)}")
        name = MODELS[base]
        sh(["ollama", "pull", base])
        sh(["ollama", "create", name, "-f", os.path.join(MODELFILES, f"{name}.Modelfile")])
        sh([py, os.path.join(PIPE, "pilot.py"), "--model", name, "--api-key", "ollama", "--out", out])
        dirs.append(os.path.join(out, name))
    finish(py, out, dirs)
    print(f"\nDone. Outputs in {out}")


if __name__ == "__main__":
    main()
