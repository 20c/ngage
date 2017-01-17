
import os
import ngage.cli
import pytest


this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, 'data')


@pytest.fixture()
def ctx():
    return ngage.cli.Context(home=os.path.join(data_dir, 'config', 'tst0'))

host_tst0='tst0.example.com'
host_tst1='tst1.example.com'
host_tst2='tst2.example.com'


def hkwa(host):
    """ make kwargs for host """
    return dict(
        host=host,
#        user='test'
        )


def test_default():
    ctx = ngage.cli.Context()
    config = ctx.get_connect_config({})
    assert config
    assert len(config)
    assert config['type']

    config = ctx.get_connect_config(hkwa(host_tst0))
    assert host_tst0 == config['host']


def test_host_exactmatch(ctx):
    config = ctx.get_connect_config(hkwa(host_tst0))
    assert "exactmatch" == config['type']
    assert host_tst0 == config['host']


def test_host_match(ctx):
    config = ctx.get_connect_config(hkwa(host_tst2))
    assert "match" == config['type']
    assert host_tst2 == config['host']


def test_host_fallthrough(ctx):
    config = ctx.get_connect_config(hkwa('notfound'))
    assert "fallthrough" == config['type']
    assert 'notfound' == config['host']


def test_host_override(ctx):
    config = ctx.get_connect_config(hkwa(host_tst1))
    assert "override" == config['type']
    assert "newhost" == config['host']
    assert "newuser" == config['user']


def test_copy_notref(ctx):
    config = ctx.get_connect_config(hkwa(host_tst1))
    config = ctx.get_connect_config(hkwa(host_tst1))
    assert "override" == config['type']
    assert "newhost" == config['host']


