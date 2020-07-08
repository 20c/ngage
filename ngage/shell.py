

import click
from cmd import Cmd
from collections import Counter
import munge
from pprint import pformat
from tabulate import tabulate


def parse_args(arg_list, keywords):
    """
    parses a list of args, for either plain args or keyword args
    args matching the keyword take the next argument as a value
    missing values or duplicate keywords throw ValueError
    returns a list and a dict
    >>> args, kwargs = parse_args(arglist, ('keya', 'keyb')
    """
    args = []
    kwargs = {}

    it = iter(arg_list)
    for each in it:
        if each not in keywords:
            args.append(each)
            continue

        if each in kwargs:
            raise ValueError("{} passed more than once".format(each))

        try:
            kwargs[each] = next(it)
        except StopIteration:
            raise ValueError("{} passed without a value".format(each))

    return args, kwargs


class BaseShell(Cmd, object):
    def __init__(self):
        super(BaseShell, self).__init__()

    def print(self, msg=None):
        click.echo(msg)

    def print_table(self, table):
        click.echo(tabulate(list(table.items()), tablefmt='plain'))

    def print_dict(self, data):
        codec = munge.get_codec('yaml')()
        click.echo(codec.dumps(data))

    def print_dict_list(self, data):
        for row in data:
            self.print_dict(row)


class Shell(BaseShell):
    def __init__(self, ctx, device=None, **kwargs):
        # break abstraction for show commands
        self.ctx = ctx
        self.device = device
        self._peers = None
        self.prompt = "{}$ ".format(device.config['host'])
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
        for addr, peer in list(peers.items()):
            if peer['is_up']:
                status = click.style('up', fg='green')
            else:
                status = click.style('down', fg='red')

            pcount = Counter()
            for each in list(peer['address_family'].values()):
                pcount += Counter(each)
            routes = "-/{}/{}/{}".format(
                pcount['accepted_prefixes'],
                pcount['received_prefixes'],
                pcount['sent_prefixes'],
                )

            data.append([addr, peer['remote_as'], status, routes])

        click.echo(tabulate(data, headers=headers, tablefmt='plain'))

    def peers(self, refresh=False):
        if not self._peers or refresh:
            self._peers = self.device.get_bgp_neighbors()
        return self._peers

    def print_routes(self, routes):
        self.print_dict_list(routes)
#    def precmd(self, line):
#    def completedefault(text, line, begidx, endidx):

    def show_bgp(self, argv):
        keywords = ('peer')
        args, kwargs = parse_args(argv, keywords)

        if len(args) != 1:
            raise ValueError("show route takes 1 argument")
        if args[0] == 'summary':
            neigh = self.peers(refresh=True)
            self.print_bgp_summary(neigh['peers'])

    def show_config(self, argv):
        config = self.device.pull()
        print(config)

    def show_route(self, argv):
        keywords = ('peer')
        args, kwargs = parse_args(argv, keywords)

        if len(args):
            if len(args) > 1:
                raise ValueError("show route takes 1 argument")
            kwargs['prefix'] = args[0]

        if 'peer' in kwargs:
            kwargs['peer'] = self.device.lookup_peer(kwargs['peer'])

        data = self.device.get_routes(**kwargs)
        self.print_routes(data)

    def do_show(self, args):
        argv = args.split(' ')

        if argv[0] == 'bgp':
            self.show_bgp(argv[1:])

        elif argv[0] == 'config':
            self.show_config(argv[1:])

        elif argv[0] == 'route':
            self.show_route(argv[1:])

        elif argv[0] == 'interfaces':
            intf = self.device.dev.get_interfaces()
            print(intf)
            self.print_table(intf)
        else:
            self.print("Unknown command {}".format(args))

        #for each in neigh:
        #    print(each)
        #    self.print_table(each)

    # aliases
    do_EOF = do_exit
