#!/bin/bash
# Portable launcher for MEDHĀ IDE
# Runs from the script's own directory; no hardcoded paths; no background web server.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use the venv if present, otherwise system python
if [[ -x ".venv/bin/python" ]]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python3"
fi

exec "$PYTHON" -m medha