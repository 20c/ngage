
import click
from ncclient import manager
from ncclient.xml_ import *

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConfigLoadError, ConnectAuthError

import getpass
import lxml
import sys


def read_files(files):
    read = list()
    for each in files:
        with open(each) as fobj:
            read.append({'file': file, 'data': fobj.read()})
    return read

def connect(host, port, user, password=None):
# https://github.com/Juniper/py-junos-eznc/blob/master/lib/jnpr/junos/utils/config.py
    try:
        jdev = Device(host, port='22', user=user, password=password)
        jdev.open()
        jdev.bind(cu=Config)
        return jdev

    except ConnectAuthError as e:
        if not password:
            password = click.prompt('password', hide_input=True)
            if password:
                return connect(host, port, user, password)
        raise


# commands : rollback, commit, show-diff-ask-commit
# diff, diff group of hosts, return value if they're different

@click.group()
@click.version_option()
@click.pass_context
#@click.argument('host', nargs=1)
def cli(ctx):
    pass
#    ctx.dev = connect(host, port=port, user=user)


def host_options(f):
    f = click.argument('host', nargs=1)(f)
    f = click.option('--user', help='username', envvar='NGAGE_USER',
                     default=getpass.getuser())(f)
    f = click.option('--password')(f)
    f = click.option('--port', default=22)(f)
    return f

def commit_options(f):
    f = click.option('--check/--no-check', help='dry run (load, commit check, rollback)', default=False)(f)
    f = click.option('--diff/--no-diff', help='show diff of changes', default=False)(f)

#  at                   Time at which to activate configuration changes
#  check                Check correctness of syntax; do not apply changes
#  comment              Message to write to commit log
#  confirmed            Automatically rollback if not confirmed
#  scripts              Push scripts to other RE
#  synchronize          Synchronize commit on both Routing Engines
    return f


def get_commit_kwargs(args):
    copy_keys = (
        'check',
        'diff',
        )
    ci_kwargs = {k: args[k] for k in copy_keys}
    return ci_kwargs


def do_commit(jdev, **kwargs):
    if kwargs['diff']:
        print jdev.cu.diff()

    if kwargs['check']:
        jdev.cu.commit_check()

#print "committing %s..." % (host,)
    jdev.cu.commit()


@cli.command()
@click.pass_context
@host_options
@commit_options
def commit(ctx, host, port, user, password, **kwargs):
    jdev = connect(host, port, user, password)
    do_commit(jdev, **get_commit_kwargs(kwargs))


@cli.command()
@click.pass_context
@host_options
@click.option('--rollback', help='rollback index', default=0)
def diff(ctx, host, port, user, password, rollback):
    jdev = connect(host, port, user, password)
    diff = jdev.cu.diff(rollback)
    if diff:
        print diff


@cli.command()
@click.pass_context
@host_options
# TODO positional?
@click.option('--index', help='rollback index', default=0)
def rollback(ctx, host, port, user, password, index):
    jdev = connect(host, port, user, password)
    jdev.cu.rollback(index)


# TODO save to file or stdout
@cli.command()
@click.pass_context
@host_options
def save(ctx, host, port, user, password):
    jdev = connect(host, port, user, password)
    options = {
        'format': 'text'
    }
    config = jdev.rpc.get_config(filter_xml=None, options=options)
    with open(host, "w") as fobj:
        print config.text
        fobj.write(config.text.encode('ascii', 'replace'))


## TODO lock option, check for uncommitted changes before commit
@cli.command()
# TODO - separate check from rollback?
@click.option('--check/--no-check', help='dry run (load, commit check, rollback)', default=False)
@click.option('--commit/--no-commit', help='commit changes',
    default=True)
@click.option('--diff/--no-diff', help='show diff of changes', default=False)
@host_options
@click.argument('files', nargs=-1)
# verbose / interactive
# atomic
def push(host, files, user, password, check, commit, diff, port):
#    host = sys.argv[1]
    print user, host, files
#        nc_commit(host, user, config)

    jdev = connect(host, port, user, password)

    try:
        # need with style for the lock
#        rsp = jdev.cu.lock()

        for each in files:
            print "loading %s..." % (each,)
            try:
                res = jdev.cu.load(path=each, format='text')
            # bogus exception on warnings
            except ConfigLoadError as e:
                # ConfigLoadError(severity: error, bad_element: policer, message: syntax error)
                # print e
                if not e.errs['severity']:
                    pass

            if diff:
                print jdev.cu.diff()

            print "checking %s..." % (each,)
            # TODO - rpc timeout if commit check and then commit
            #jdev.cu.commit_check()

        if check:
            jdev.cu.rollback()
        elif commit:
            # throws on warnings / errors
            #jdev.cu.commit_check()
            print "committing %s..." % (host,)
            jdev.cu.commit()

    except Exception as e:
        print "push error", e
        print jdev.cu.diff()
        jdev.cu.rollback()
#        jdev.cu.unlock()


#    jdev.cu.rollback()
#    jdev.cu.unlock()

