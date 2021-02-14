import fnmatch
import getpass
import logging
import os

import click
import munge.click
import munge.util

import ngage
import ngage.shell
from ngage.exceptions import AuthenticationError


def make_get_options(*keys):
    def getter(kwargs):
        return {k: kwargs.pop(k, None) for k in keys}

    return getter


def connect_options(f):
    f = click.argument("host", nargs=1)(f)
    f = click.option("--port", help="port to connect to, default per platform")(f)
    f = click.option("--type", help="type of connection")(f)
    f = click.option("--user", help="username", envvar="NGAGE_USER")(f)
    f = click.option("--password", help="password to use if not using key auth")(f)
    return f


get_connect_options = make_get_options("host", "port", "type", "user", "password")


def update_context(ctx, kwargs):
    """ updates context from current command line args, then reinits """
    ctx.update_options(kwargs)

    if not isinstance(ctx.config["ngage"]["plugin_path"], list):
        raise ValueError("config item ngage.plugin_path must be a list")
    # set plugin search path to defined + $home/plugins
    searchpath = ctx.config["ngage"]["plugin_path"]
    if ctx.home:
        searchpath.append(os.path.join(ctx.home, "plugins"))
    ngage.plugin.searchpath = searchpath


class Context(munge.click.Context):
    app_name = "ngage"
    config_class = ngage.Config

    @property
    def log(self):
        if not getattr(self, "_logger", None):
            self._logger = logging.getLogger("ngage")
        return self._logger

    def init(self):
        super().init()

        # only print our log messages
        for handler in logging.getLogger().handlers:
            # handler.addFilter(logging.Filter('pybird'))
            handler.addFilter(logging.Filter(self.app_name))

    def get_host_config(self, target, config):
        # look for host config
        for each in self.config["ngage"]["hosts"]:
            host = each.get("host", None)
            if not host:
                continue
            if host == target or fnmatch.fnmatch(target, host):
                munge.util.recursive_update(config, each, copy=True)
                break

    def get_connect_config(self, kwargs):
        # get default config
        config = self.config["ngage"]["default"].copy()
        # leave host on kwargs so it will override and matched config
        target = kwargs.get("host", None)

        if target:
            self.get_host_config(target, config)

        # overlay kwargs on default and remove them from kwargs
        for k, v in list(get_connect_options(kwargs).items()):
            if v:
                config[k] = v

        # overwrite if hostname is set
        if "hostname" in config:
            config["host"] = config.pop("hostname")

        if not config.get("user", None):
            config["user"] = getpass.getuser()

        return config

    def connect(self, kwargs):
        try:
            # get config
            config = self.get_connect_config(kwargs)

            typ = config["type"]
            # check for subtype
            if ":" in typ:
                typ = config["type"].split(":", 1)[0]

            cls = ngage.plugin.get_plugin_class(typ)
            drv = cls(config)
            self.log.debug("connecting to {host}".format(**config))
            drv.open()
            return drv

        except AuthenticationError:
            config["password"] = click.prompt("password", hide_input=True)
            if config["password"]:
                return connect(config)
            raise


@click.group()
@Context.pass_context()
@click.version_option()
# @common_options
def cli(ctx, **kwargs):
    update_context(ctx, kwargs)


@cli.command()
@Context.pass_context()
@Context.options
@click.option(
    "--write",
    help="write config, if home is not specified, uses cwd",
    is_flag=True,
    default=False,
)
def config(ctx, **kwargs):
    """ view and interact with the config """
    update_context(ctx, kwargs)

    meta = ctx.config.meta
    if meta:
        ctx.log.info("config loaded from %s", meta["config_dir"])
    else:
        ctx.log.info("no config loaded")

    if kwargs.get("write"):
        config_dir = ctx.home if ctx.home else ".ngage"
        ctx.log.info("writing config to '%s'", config_dir)
        ctx.config.write(config_dir)
        return

    if ctx.home:
        home = ctx.home
    else:
        home = "defaults, no home set (--write will create .ngage)"
    click.echo("current config from %s" % home)
    click.echo(ctx.config.data)


@cli.command()
@Context.pass_context()
@connect_options
@click.option(
    "--check/--no-check", help="check config but do not do actual commit", default=False
)
@click.option("--diff/--no-diff", help="show diff of changes", default=False)
def commit(ctx, **kwargs):
    """ commit changes on a device """
    update_context(ctx, kwargs)
    dev = ctx.connect(kwargs)

    if kwargs["diff"]:
        click.echo(dev.diff())

    if kwargs["check"]:
        dev.check()
    else:
        dev.commit()


@cli.command()
@Context.pass_context()
@connect_options
@click.option("--index", help="rollback index", default=0)
def diff(ctx, **kwargs):
    """ get diff from device """
    update_context(ctx, kwargs)
    dev = ctx.connect(kwargs)

    diff = dev.diff(**kwargs)
    click.echo(diff)


@cli.command()
@Context.pass_context()
@connect_options
@click.option("--index", help="rollback index", default=0)
def rollback(ctx, **kwargs):
    """ rollback device config """
    update_context(ctx, kwargs)
    dev = ctx.connect(kwargs)

    dev.rollback(**kwargs)


@cli.command()
@Context.pass_context()
@Context.options
@connect_options
@click.option(
    "--output-dir",
    help="directory to save file to, will be named from filename option",
    default=".",
)
@click.argument("filename", default="-")
def pull(ctx, filename, **kwargs):
    """ pull config from a device """
    # set filename before kwargs get mangled
    if filename != "-":
        filename = filename.format(**kwargs)
        filename = os.path.join(kwargs["output_dir"], filename)

    update_context(ctx, kwargs)

    dev = ctx.connect(kwargs)
    config = dev.pull()

    with click.open_file(filename, "wb") as fobj:
        fobj.write(config)


@cli.command()
@Context.pass_context()
@Context.options
@connect_options
@click.option("--check/--no-check", help="commit check config", default=True)
@click.option("--commit/--no-commit", help="commit changes", default=False)
@click.option("--diff/--no-diff", help="show diff of changes", default=False)
@click.option("--lock/--no-lock", help="lock config for exclusive access", default=True)
@click.option(
    "--rollback/--no-rollback", help="rollback changes after push", default=False
)
@click.argument("files", nargs=-1)
def push(ctx, files, **kwargs):
    """ push config to a device """
    update_context(ctx, kwargs)
    dev = ctx.connect(kwargs)

    try:
        check = kwargs["check"]
        commit = kwargs["commit"]
        diff = kwargs["diff"]
        lock = kwargs["lock"]
        rollback = kwargs["rollback"]

        if rollback and commit:
            ctx.error("cannot have both commit and rollback")
            return 1

        if lock:
            dev.lock()

        # nested try to allow for rollback on push errors
        try:
            for each in files:
                ctx.log.info(f"pushing {each}")
                dev.push(each)
                if diff:
                    click.echo(dev.diff())

                if check:
                    dev.check()

        except Exception as e:
            if rollback:
                dev.rollback()
            raise

        if rollback:
            ctx.log.info(f"rollback {dev.host}")
            dev.rollback()

        elif commit:
            ctx.log.info(f"committing {dev.host}")
            dev.commit()

    except Exception as e:
        ctx.log.error("push error %s", e)
        ctx.log.info(dev.diff())
        raise

    finally:
        if lock:
            dev.unlock()


@cli.command()
@Context.pass_context()
@Context.options
@connect_options
@click.option("--check/--no-check", help="commit check config", default=True)
@click.option("--commit/--no-commit", help="commit changes", default=False)
@click.option("--diff/--no-diff", help="show diff of changes", default=False)
@click.option("--lock/--no-lock", help="lock config for exclusive access", default=True)
@click.option(
    "--rollback/--no-rollback", help="rollback changes after push", default=False
)
@click.argument("command", nargs=-1)
def shell(ctx, command=(), **kwargs):
    update_context(ctx, kwargs)

    dev = ctx.connect(kwargs)
    shell = ngage.shell.Shell(ctx, device=dev, **kwargs)
    if not command:
        shell.cmdloop()
    else:
        cmd = " ".join(command)
        shell.onecmd(cmd)
