from __future__ import absolute_import
from __future__ import print_function

import click
import getpass
import os
import sys

import ngage
from ngage.config import Config
from ngage.exceptions import AuthenticationError


def connect(kwargs):
    try:
        # get connect specific options and remove them from kwargs
        config = get_connect_options(kwargs)
        cls = ngage.plugin.get_plugin_class(config['type'])
        drv = cls(config)
        drv.open()
        return drv

    except AuthenticationError:
        config['password'] = click.prompt('password', hide_input=True)
        if config['password']:
            return connect(config)
        raise

def make_get_options(*keys):
    def getter(kwargs):
        return {k: kwargs.pop(k, None) for k in keys}
    return getter


def connect_options(f):
    f = click.argument('host', nargs=1)(f)
    f = click.option('--port', help='port to connect to, default per platform')(f)
    f = click.option('--type', help='type of connection, default eznc', default='eznc')(f)
    f = click.option('--user', help='username', envvar='NGAGE_USER',
                     default=getpass.getuser())(f)
    f = click.option('--password', help='password to use if not using key auth')(f)
    return f


get_connect_options = make_get_options('host', 'port', 'type', 'user', 'password')


class Context(object):
    # all levels of commands will use/process these
    @classmethod
    def options(cls, f):
        f = click.version_option()(f)
        f = click.option('--debug', help='enable extra debug output', is_flag=True, default=None)(f)
        f = click.option('--home', help='by default will check in order: $NGAGE_HOME, ./.ngage, ' + click.get_app_dir('ngage'), envvar='NGAGE_HOME', default=None)(f)
        f = click.option('--verbose', help='enable more verbose output', is_flag=True, default=None)(f)
        return f

    @classmethod
    def get_options(cls, kwargs):
        keys = ('debug', 'home', 'verbose')
        return {k: kwargs.pop(k, None) for k in keys}

    @classmethod
    def pass_context(cls):
        return click.make_pass_decorator(cls, ensure=True)

    def __init__(self, **kwargs):
        self.debug = False
        self.quiet = False
        self.verbose = False

        self.home = None
        self.config = None

        self.update_options(kwargs)

    def update_options(self, kwargs):
        opt = self.__class__.get_options(kwargs)

        if opt.get('debug', None) is not None:
            self.debug = opt['debug']

        if opt.get('verbose', None) is not None:
            self.verbose = opt['verbose']

        if opt.get('home', None) is not None:
            self.home = opt['home']
            self.config = None

        search_path = [os.path.join('.', '.ngage'),
                       click.get_app_dir('ngage')]
        if self.home:
            search_path.insert(self.home, 0)

        if not self.config:
            self.config = Config(try_read=search_path)

    def msg(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    def print(self, msg, *args):
        """logs a message to stderr unless quiet is enabled"""
        if not self.quiet:
            self.msg(msg, *args)

    def vprint(self, msg, *args):
        """logs a message to stderr only if debug is enabled"""
        if self.verbose:
            self.msg(msg, *args)

    def dprint(self, msg, *args):
        """logs a message to stderr only if debug is enabled"""
        if self.debug:
            self.msg(msg, *args)


@click.group()
@Context.pass_context()
#@common_options
def cli(ctx, **kwargs):
    ctx.update_options(kwargs)


@cli.command()
@Context.pass_context()
@Context.options
@click.option('--write', help='write config, if home is not specified, uses cwd', is_flag=True, default=False)
def config(ctx, **kwargs):
    """ view and interact with the config """
    ctx.update_options(kwargs)

    meta = ctx.config.meta
    if meta:
        ctx.print("config loaded from %s", meta['config_dir'])
    else:
        ctx.print("no config loaded")

    if kwargs.get('write'):
        config_dir = ctx.home if ctx.home else ".ngage"
        ctx.print("writing config to '%s'", config_dir)
        ctx.config.write(config_dir)
        return

    ctx.vprint('current config')
    ctx.vprint(ctx.config.data)


@cli.command()
@Context.pass_context()
@connect_options
@click.option('--check/--no-check', help='check config but do not do actual commit', default=False)
@click.option('--diff/--no-diff', help='show diff of changes', default=False)
def commit(ctx, **kwargs):
    """ commit changes on a device """
    ctx.update_options(kwargs)
    dev = connect(kwargs)

    if kwargs['diff']:
        ctx.print(dev.diff())

    if kwargs['check']:
        dev.check()
    else:
        dev.commit()


@cli.command()
@Context.pass_context()
@connect_options
@click.option('--index', help='rollback index', default=0)
def diff(ctx, **kwargs):
    """ get diff from device """
    ctx.update_options(kwargs)
    dev = connect(kwargs)

    diff = dev.diff(**kwargs)
    ctx.print(diff)


@cli.command()
@Context.pass_context()
@connect_options
@click.option('--index', help='rollback index', default=0)
def rollback(ctx, **kwargs):
    """ rollback device config """
    ctx.update_options(kwargs)
    dev = connect(kwargs)

    dev.rollback(**kwargs)


@cli.command()
@Context.pass_context()
@Context.options
@connect_options
@click.option('--output-dir', help='directory to save file to, will be named from filename option', default='.')
@click.argument('filename', default='-')
def pull(ctx, filename, **kwargs):
    """ pull config from a device """
    # set filename before kwargs get mangled
    if filename != '-':
        filename = filename.format(**kwargs)
        filename = os.path.join(kwargs['output_dir'], filename)

    ctx.update_options(kwargs)

    dev = connect(kwargs)
    config = dev.pull(**kwargs)

    with click.open_file(filename, 'w') as fobj:
        fobj.write(config)


@cli.command()
@Context.pass_context()
@Context.options
@connect_options
@click.option('--check/--no-check', help='commit check config', default=True)
@click.option('--commit/--no-commit', help='commit changes', default=False)
@click.option('--diff/--no-diff', help='show diff of changes', default=False)
@click.option('--lock/--no-lock', help='lock config for exclusive access', default=True)
@click.option('--rollback/--no-rollback', help='rollback changes after push', default=False)
@click.argument('files', nargs=-1)
def push(ctx, files, **kwargs):
    """ push config to a device """
    ctx.update_options(kwargs)
    dev = connect(kwargs)

    try:
        check = kwargs['check']
        commit = kwargs['commit']
        diff = kwargs['diff']
        lock = kwargs['lock']
        rollback = kwargs['rollback']

        if rollback and commit:
            ctx.print("cannot have both commit and rollback")
            return 1

        if lock:
            dev.lock()

        # nested try to allow for rollback on push errors
        try:
            for each in files:
                ctx.vprint("pushing %s" % (each,))
                dev.push(each)
                if diff:
                    ctx.print(dev.diff())

                dev.check()
                if check:
                    dev.check()

        except Exception as e:
            if rollback:
                dev.rollback()
            raise

        if rollback:
            ctx.vprint("rollback %s" % (dev.host,))
            dev.rollback()

        elif commit:
            ctx.vprint("committing %s" % (dev.host,))
            dev.commit()

    except Exception as e:
        ctx.print("push error %s", e)
        ctx.vprint(dev.diff())
        raise

    finally:
        if lock:
            dev.unlock()

