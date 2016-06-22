
import ngage.cli

from click.testing import CliRunner
import pytest


def test_cli():
    runner = CliRunner()
    rv = runner.invoke(ngage.cli.cli, [])
    assert 0 == rv.exit_code

