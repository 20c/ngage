from __future__ import absolute_import

import ngage
from ngage.exceptions import AuthenticationError, ConfigError

import ipaddress
from pybird import PyBird


@ngage.plugin.register('bird')
class Driver(ngage.plugins.DriverPlugin):
    plugin_type = 'bird'

    def _do_init(self):
        config = self.config

        self.host = config.get('host')
        self.user = config.get('user')
        self.password = config.get('password')
        self.optional_args = config.get('driver_args', {})

        socket_file = self.optional_args.pop('socket_file', None)
        if not socket_file:
            raise ValueError('bird requires socket_file in driver_args')

        self.dev = PyBird(socket_file, self.host, self.user, self.password)

    def _do_open(self):
        # TODO connection caching
        return
        try:
            self.dev.open()

        except ConnectionException:
            raise AuthenticationError

    def _do_close(self):
        self.dev.close()

    def _do_pull(self):
        if not hasattr(self.dev, 'get_config'):
            raise NotImplementedError('get_config not implemented, please update napalm')
        return self.dev.get_config(retrieve='candidate')['candidate']

    def _do_push(self, fname, **kwargs):
        try:
            self.dev.load_merge_candidate(filename=fname)

        except (MergeConfigException, ReplaceConfigException) as e:
            raise ConfigError(e.message)

    def _do_diff(self, index=0):
        if index != 0:
            raise NotImplementedError('version index not implemented')
        return self.dev.compare_config()

    def _do_lock(self):
        self.dev.lock()

    def _do_unlock(self):
        self.dev.unlock()

    def _do_commit(self, **kwargs):
        self.dev.commit_config()

#    def _do_check(self):
# not impl by napalm

    def _do_rollback(self, index=0):
        if index == 0:
            self.dev.discard_config()
        elif index == 1:
            self.dev.rollback()
        else:
            raise NotImplementedError('version index not implemented')

    def _do_get_bgp_neighbors(self):
        router_id = self.dev.get_bird_status().get('router_id', '')

        field_map = {
            # 'local_as'
            'asn': 'remote_as',
            'router_id': 'remote_id',
            'up': 'is_up',
            'description': 'description',
            # 'uptime'
            }

        rv = {
            'router_id': router_id,
            'peers': {},
            }

        for peer in self.dev.get_peer_status():
            if peer['protocol'] != 'BGP':
                continue

            # TODO use inet abstraction
            addr = ipaddress.ip_address(unicode(peer['address']))

            row = {v: peer.get(k, None) for k, v in field_map.items()}
            row['is_enabled'] = True
            row['address_family'] = {
                'ipv{}'.format(addr.version): {
                    'received_prefixes': 0,
                    'accepted_prefixes': peer['routes_imported'],
                    'sent_prefixes': peer['routes_exported'],
                    }
                }
            rv['peers'][addr] = row

        return rv

    def _do_get_routes(self):
        routes = self.dev.get_routes()
        return routes

