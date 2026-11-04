"""Offline by default: only explicitly opted-in tests may contact the registry.

This file is imported by pytest before any test collection. Setting
QT_QPA_PLATFORM=offscreen here ensures the Qt application never tries to open
a real display, so the entire test suite runs headless on CI and local machines
without a window server.
"""
import os

# Set offscreen platform BEFORE any Qt import happens — this must be at the very top
# so that terminal.py, app.py, and all other modules that import QtWidgets at
# module level never attempt to connect to a display server.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


def pytest_configure(config):
    config.addinivalue_line('markers', 'network: requires external internet access')


def pytest_collection_modifyitems(config, items):
    # Local fake HTTP servers remain enabled; only real external calls need opt-in.
    if os.environ.get('MEDHA_NETWORK_TESTS') != '1':
        for item in items:
            if item.get_closest_marker('network'):
                item.add_marker(pytest.mark.skip(reason='Set MEDHA_NETWORK_TESTS=1 for network tests'))
