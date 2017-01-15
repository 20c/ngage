from __future__ import print_function

import click
from cmd import Cmd
from collections import Counter
import munge
from pprint import pformat
from tabulate import tabulate


class BaseShell(Cmd, object):
    def __init__(self):
        super(BaseShell, self).__init__()

    def print(self, msg=None):
        click.echo(msg)

    def print_table(self, table):
        click.echo(tabulate(table.items(), tablefmt='plain'))

    def print_dict(self, data):
        codec = munge.get_codec('yaml')()
        click.echo(codec.dumps(data))


class Shell(BaseShell):
    def __init__(self, ctx, device=None, **kwargs):
        # break abstraction for show commands
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
        self.print_table(self.ctx.config.meta)
        self.print()
        self.print("Config")
        self.print_dict(self.ctx.config.data)

    def print_bgp_summary(self, peers):
        headers = ['Peer', 'AS', 'Status', 'Active/Accepted/Received/Sent']
        data = []
        for addr, peer in peers.items():
            if peer['is_up']:
                status = click.style('up', fg='green')
            else:
                status = click.style('down', fg='red')

            pcount = Counter()
            for each in peer['address_family'].values():
                pcount += Counter(each)
            routes = "-/{}/{}/{}".format(
                pcount['accepted_prefixes'],
                pcount['received_prefixes'],
                pcount['sent_prefixes'],
                )

            data.append([addr, peer['remote_as'], status, routes])

        click.echo(tabulate(data, headers=headers, tablefmt='plain'))

#    def precmd(self, line):
#    def completedefault(text, line, begidx, endidx):

    def do_show(self, args):
        if args == 'bgp':
            neigh = self.device.get_bgp_neighbors()
            self.print_bgp_summary(neigh['peers'])

        elif args == 'interfaces':
            intf = self.device.dev.get_interfaces()
            print(intf)
            self.print_table(intf)
        else:
            self.print("Unknown command")

        #for each in neigh:
        #    print(each)
        #    self.print_table(each)

    # aliases
    do_EOF = do_exit
