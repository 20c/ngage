import pytest

import ngage


default_config = {
    'host': 'localhost',
    'type': 'napalm:junos'
    }

@pytest.fixture()
def cls():
    return ngage.plugin.get_plugin_class('napalm')


@pytest.fixture()
def obj(cls):
    return cls(default_config)


def test_init(cls):
    assert cls(default_config)


def test_init_no_subtype(cls):
    with pytest.raises(ValueError):
        cls({'type': 'napalm'})


def test_notimpl(obj):
    with pytest.raises(NotImplementedError):
        obj.check()
