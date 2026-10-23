# PyInstaller entry point: same as `python -m medha` (keeps --version / --selftest).
import sys
from medha.__main__ import main
sys.exit(main())
