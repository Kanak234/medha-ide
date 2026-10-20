#!/bin/bash
# ==============================================================================
# MEDHĀ STUDIO — System Verification & Launcher Script
# ==============================================================================

echo "=============================================================="
echo "MEDHĀ STUDIO — SYSTEM DEPENDENCY & LAUNCH CHECK"
echo "=============================================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check System Dependencies
check_tool() {
    if command -v "$1" &> /dev/null; then
        echo "  [OK] $1 detected: $(which $1)"
    else
        echo "  [WARNING] $1 not found! Install via: sudo apt install $2"
    fi
}

check_tool gcc build-essential
check_tool python3 python3
check_tool javac default-jdk

python3 -c "import PySide6" &> /dev/null
if [ $? -eq 0 ]; then
    echo "  [OK] PySide6 Python package detected."
else
    echo "  [WARNING] PySide6 not installed! Install via: sudo apt install python3-pyside6"
fi

echo "=============================================================="
echo "Launching MEDHĀ Studio..."
echo "=============================================================="

python3 "$SCRIPT_DIR/app.py"
