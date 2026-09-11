# Contributing to MEDHĀ IDE

Thank you for contributing to MEDHĀ IDE, a native desktop IDE suite for C, C++, Python, and Java development.

## Code of Conduct

All participants must maintain a welcoming, respectful, and productive environment.

## Development Environment Setup

### 1. Prerequisites
- **Python**: 3.10 or higher
- **PySide6**: 6.5 or higher
- **System Toolchains**: `gcc`, `g++`, `gdb`, `git`, `cmake`, `make`

### 2. Installation
```bash
git clone https://github.com/Kanak234/medha-ide.git
cd medha-ide
pip install -e .[test]
```

### 3. Testing and Verification
```bash
# Run pytest with strict coverage gate (>=80%)
pytest --cov --cov-fail-under=80

# Run self-diagnostic health check
python3 -m medha health

# Run P3-P6 verification harness
python3 verify_medha_p3_p6.py

# Run DSA visualizer verification
python3 verify_dsa_visualizer.py
```

### 4. Quality Standards
- **Zero Mock Data**: Never hardcode dummy test data, mock returns, or synthetic simulations in production pathways.
- **Coverage**: Keep core domain logic covered >= 80%.
- **Safety**: Ensure code changes pass compiler syntax checks and static analysis.

## Submitting Pull Requests

1. Branch from `master` with an informative branch name.
2. Verify all test suites pass locally.
3. Open a Pull Request detailing the purpose, changes, and verification evidence.
