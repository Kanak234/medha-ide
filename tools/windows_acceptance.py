"""Run the same acceptance used by MEDHA.exe --acceptance on a source checkout."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from medha.release_acceptance import main

if __name__ == '__main__':
    sys.exit(main())
