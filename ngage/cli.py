from __future__ import absolute_import
from __future__ import print_function

import click
import getpass
import logging
import os

import ngage
from ngage.exceptions import AuthenticationError
import munge.click


def connect(kwargs):
    try:
        # get connect specific options and remove them from kwargs
        config = get_connect_options(kwargs)

        typ = config['type']
        # check for subtype
        if ':' in typ:
            (typ, na) = config['type'].split(':', 1)

        cls = ngage.plugin.get_plugin_class(typ)
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


def update_context(ctx, kwargs):
    """ updates context from current command line args, then reinits """
    ctx.update_options(kwargs)

    if not isinstance(ctx.config['ngage']['plugin_path'], list):
        raise ValueError('config item ngage.plugin_path must be a list')
    # set plugin search path to defined + $home/plugins
    searchpath = ctx.config['ngage']['plugin_path']
    if ctx.home:
        searchpath.append(os.path.join(ctx.home, 'plugins'))
    ngage.plugin.searchpath = searchpath


class Context(munge.click.Context):
    app_name = 'ngage'
    config_class = ngage.Config

    @property
    def log(self):
        if not getattr(self, '_logger', None):
            self._logger = logging.getLogger('ngage')
        return self._logger


@click.group()
@Context.pass_context()
#@common_options
def cli(ctx, **kwargs):
    update_context(ctx, kwargs)


@cli.command()
@Context.pass_context()
@Context.options
@click.option('--write', help='write config, if home is not specified, uses cwd', is_flag=True, default=False)
def config(ctx, **kwargs):
    """ view and interact with the config """
    update_context(ctx, kwargs)

    meta = ctx.config.meta
    if meta:
        ctx.log.info("config loaded from %s", meta['config_dir'])
    else:
        ctx.log.info("no config loaded")

    if kwargs.get('write'):
        config_dir = ctx.home if ctx.home else ".ngage"
        ctx.log.info("writing config to '%s'", config_dir)
        ctx.config.write(config_dir)
        return

    if ctx.home:
        home = ctx.home
    else:
        home = 'defaults, no home set (--write will create .ngage)'
    click.echo('current config from %s' % home)
    click.echo(ctx.config.data)


@cli.command()
@Context.pass_context()
@connect_options
@click.option('--check/--no-check', help='check config but do not do actual commit', default=False)
@click.option('--diff/--no-diff', help='show diff of changes', default=False)
def commit(ctx, **kwargs):
    """ commit changes on a device """
    update_context(ctx, kwargs)
    dev = connect(kwargs)

    if kwargs['diff']:
        click.echo(dev.diff())

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
    update_context(ctx, kwargs)
    dev = connect(kwargs)

    diff = dev.diff(**kwargs)
    click.echo(diff)


@cli.command()
@Context.pass_context()
@connect_options
@click.option('--index', help='rollback index', default=0)
def rollback(ctx, **kwargs):
    """ rollback device config """
    update_context(ctx, kwargs)
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

    update_context(ctx, kwargs)

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
    update_context(ctx, kwargs)
    dev = connect(kwargs)

    try:
        check = kwargs['check']
        commit = kwargs['commit']
        diff = kwargs['diff']
        lock = kwargs['lock']
        rollback = kwargs['rollback']

        if rollback and commit:
            ctx.error("cannot have both commit and rollback")
            return 1

        if lock:
            dev.lock()

        # nested try to allow for rollback on push errors
        try:
            for each in files:
                ctx.log.info("pushing %s" % (each,))
                dev.push(each)
                if diff:
                    click.echo(dev.diff())

                dev.check()
                if check:
                    dev.check()

        except Exception as e:
            if rollback:
                dev.rollback()
            raise

        if rollback:
            ctx.log.info("rollback %s" % (dev.host,))
            dev.rollback()

        elif commit:
            ctx.log.info("committing %s" % (dev.host,))
            dev.commit()

    except Exception as e:
        ctx.log.error("push error %s", e)
        ctx.log.info(dev.diff())
        raise

    finally:
        if lock:
            dev.unlock()

