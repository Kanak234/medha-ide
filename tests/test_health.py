import sys
import pytest
from medha.__main__ import health_check, main

def test_health_check_returns_zero(capsys):
    ret = health_check()
    assert ret == 0
    captured = capsys.readouterr()
    assert '"status": "ok"' in captured.out
    assert '"app": "medha-ide"' in captured.out

def test_main_health_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["medha", "--health"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
