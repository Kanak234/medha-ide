# Windowed PyInstaller apps have no console. Keep startup exceptions in user data.
import sys
import traceback
from medha.platform_info import user_data_dir

log = (user_data_dir() / "startup.log").open("a", encoding="utf-8", buffering=1)
if sys.stdout is None:
    sys.stdout = log
if sys.stderr is None:
    sys.stderr = log
try:
    from medha.__main__ import main
    sys.exit(main())
except Exception:
    traceback.print_exc(file=log)
    raise
