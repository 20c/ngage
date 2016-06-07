from __future__ import print_function

import click
import getpass
import os
import sys

from ngage.exceptions import AuthenticationError
from ngage.plugins.eznc import EzncDriver as Driver


def connect(kwargs):
    try:
        # get connect specific options and remove them from kwargs
        config = get_connect_config(kwargs)
        drv = Driver(config)
        drv.open()
        return drv

    except AuthenticationError as e:
        if not password:
            password = click.prompt('password', hide_input=True)
            if password:
                return connect(host, port, user, password)
        raise


def common_options(f):
    f = click.version_option(f)
    return f


def connect_options(f):
    f = click.argument('host', nargs=1)(f)
    f = click.option('--port', help='port to connect to, default per platform')(f)
    f = click.option('--user', help='username', envvar='NGAGE_USER',
                     default=getpass.getuser())(f)
    f = click.option('--password', help='password to use if not using key auth')(f)
    return f


def get_connect_config(kwargs):
    keys = (
        'host',
        'port',
        'user',
        'password',
        )
    return {k: kwargs.pop(k, None) for k in keys}


@click.group()
#@common_options
@click.version_option()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.pass_context
@connect_options
@click.option('--check/--no-check', help='check config but do not do actual commit', default=False)
@click.option('--diff/--no-diff', help='show diff of changes', default=False)
def commit(ctx, **kwargs):
    dev = connect(kwargs)

    if kwargs['diff']:
        print(dev.diff())

    if kwargs['check']:
        dev.check()
    else:
        dev.commit()


@cli.command()
@click.pass_context
@connect_options
@click.option('--index', help='rollback index', default=0)
def diff(ctx, **kwargs):
    dev = connect(kwargs)
    diff = dev.diff(**kwargs)
    print(diff)


@cli.command()
@click.pass_context
@connect_options
@click.option('--index', help='rollback index', default=0)
def rollback(ctx, **kwargs):
    dev = connect(kwargs)
    dev.rollback(**kwargs)


@cli.command()
@click.pass_context
@connect_options
@click.option('--output-dir', help='directory to save file to, will be named from filename option', default='.')
@click.argument('filename', default='-')
def pull(ctx, filename, **kwargs):
    # set filename before kwargs get mangled
    if filename != '-':
        filename = filename.format(**kwargs)
        filename = os.path.join(kwargs['output_dir'], filename)

    dev = connect(kwargs)
    config = dev.pull(**kwargs)

    with click.open_file(filename, 'w') as fobj:
        fobj.write(config)


@cli.command()
@click.pass_context
@connect_options
@click.option('--check/--no-check', help='commit check config', default=True)
@click.option('--commit/--no-commit', help='commit changes', default=False)
@click.option('--diff/--no-diff', help='show diff of changes', default=False)
@click.option('--lock/--no-lock', help='lock config for exclusive access', default=True)
@click.option('--rollback/--no-rollback', help='rollback changes after push', default=False)
@click.argument('files', nargs=-1)
def push(ctx, files, **kwargs):
    dev = connect(kwargs)

    try:
        check = kwargs['check']
        commit = kwargs['commit']
        diff = kwargs['diff']
        lock = kwargs['lock']
        rollback = kwargs['rollback']

        if rollback and commit:
            print("cannot have both commit and rollback")
            return 1

        if lock:
            dev.lock()

        # nested try to allow for rollback on push errors
        try:
            for each in files:
                print("pushing %s" % (each,))
                dev.push(each)
                if diff:
                    print(dev.diff())

                dev.check()
                if check:
                    dev.check()

        except Exception as e:
            if rollback:
                dev.rollback()
            raise

        if rollback:
            print("rollback %s" % (dev.host,))
            dev.rollback()

        elif commit:
            print("committing %s" % (dev.host,))
            dev.commit()

    except Exception as e:
        print("push error", e)
        print(dev.diff())
        raise

    finally:
        if lock:
            dev.unlock()

