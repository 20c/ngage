from __future__ import print_function

import click
from cmd import Cmd
from pprint import pformat
from tabulate import tabulate


class BaseShell(Cmd, object):
    def __init__(self):
        super(BaseShell, self).__init__()

    def print(self, msg=None):
        click.echo(msg)

    def print_table(self, table):
        click.echo(tabulate(table.items(), tablefmt='plain'))



class Shell(BaseShell):
    def __init__(self, ctx, device=None, **kwargs):
        # break abstraction for show commands
        if device.plugin_type != 'napalm':
            raise NotImplementedError("shell only supported on napalm connections")
        self.ctx = ctx
        self.device = device
        super(Shell, self).__init__()

    # don't repeat command on empty line
    def emptyline(self):
        pass

    def do_exit(self, s):
        if s:
            return False
        self.print()
        return True

    def help_exit(self):
        self.print("Exit the interpreter")
        self.print("You can also use the Ctrl-D shortcut")

    def do_ngage(self, args):
        self.print("Config meta:")
        self.print_table(self.ctx.config.meta.items())
        self.print()
        self.print("Config")
        self.print(tabulate(self.ctx.config.items(), tablefmt='plain'))

    def do_show(self, args):
        # TODO nested cmds
        if args == 'bgp':
            neigh = self.device.dev.get_bgp_neighbors()
        elif args == 'interfaces':
            neigh = self.device.dev.get_interfaces()
        else:
            self.print("Unknown command")

        #for each in neigh:
        #    print(each)
        #    self.print_table(each)
        self.print_table(neigh)

    # aliases
    do_EOF = do_exit
