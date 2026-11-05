# Keep startup exceptions in user data, including launches without standard streams.
import sys
import traceback
from medha.platform_info import user_data_dir

log = (user_data_dir() / "startup.log").open("a", encoding="utf-8", buffering=1)
if sys.stdout is None:
    sys.stdout = log
if sys.stderr is None:
    sys.stderr = log
# Attached build pipes may use cp1252 even though logs use UTF-8. Compiler
# output includes MEDHĀ and Unicode diagnostics; preserve them in both modes.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")
try:
    from medha.__main__ import main
    sys.exit(main())
except Exception:
    traceback.print_exc(file=log)
    raise
