"""Repository paths used by every script, so the code runs from any working directory."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INJECAGENT = os.path.join(REPO, "data", "injecagent")   # bundled InjecAgent files (commit f19c9f2, MIT licence)
MODELFILES = os.path.join(REPO, "modelfiles")           # Ollama Modelfiles that set an 8,192-token context
RESULTS = os.path.join(REPO, "results")                 # published results (read-only)
RAW = os.path.join(RESULTS, "raw")                      # published raw model outputs, one folder per model
OUTPUTS = os.path.join(REPO, "outputs")                 # default location for new runs (never overwrites results/)
