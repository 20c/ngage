import pytest
from click.testing import CliRunner

import ngage.cli

commands = ("commit", "config", "diff", "pull", "push", "rollback")


def test_cli():
    runner = CliRunner()
    rv = runner.invoke(ngage.cli.cli, [])
    assert 0 == rv.exit_code


def test_cli_invoke():
    pass
    runner = CliRunner()
    for cmd in commands:
        res = runner.invoke(ngage.cli.cli, [cmd])
        assert res.exit_code in (0, 2)
