from __future__ import absolute_import

import ngage
from ngage.exceptions import AuthenticationError, ConfigError

import napalm
from napalm_base.exceptions import (
    ConnectionException,
    ReplaceConfigException,
    MergeConfigException
)


@ngage.plugin.register('napalm')
class Driver(ngage.plugins.DriverPlugin):
    plugin_type = 'napalm'

    def _do_init(self):
        config = self.config

        self.host = config.get('host')
        self.user = config.get('user')
        self.password = config.get('password')

        if ':' not in config['type']:
            raise ValueError('napalm requires a subtype')

        (na, driver) = config['type'].split(':', 2)
        cls = napalm.get_network_driver(driver)
        self.dev = cls(self.host, self.user, self.password)

    def _do_open(self):
        try:
            self.dev.open()

        except ConnectionException:
            raise AuthenticationError

    def _do_close(self):
        self.dev.close()

#    def _do_pull(self):
# not impl by napalm

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

