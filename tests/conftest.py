"""Offline by default: only explicitly opted-in tests may contact the registry."""
import os
import pytest


def pytest_configure(config):
    config.addinivalue_line('markers', 'network: requires external internet access')


def pytest_collection_modifyitems(config, items):
    # Local fake HTTP servers remain enabled; only real external calls need opt-in.
    if os.environ.get('MEDHA_NETWORK_TESTS') != '1':
        for item in items:
            if item.get_closest_marker('network'):
                item.add_marker(pytest.mark.skip(reason='Set MEDHA_NETWORK_TESTS=1 for network tests'))
