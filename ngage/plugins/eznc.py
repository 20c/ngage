#from __future__ import absolute_import

import ngage
from ngage.exceptions import AuthenticationError

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConfigLoadError, ConnectAuthError


class EzncDriver(ngage.plugins.DriverPlugin):
    plugin_type = 'eznc'

    def _do_init(self):
        config = self.config

        self.host = config.get('host')
        self.port = config.get('port', 22)
        if not self.port:
            self.port = 22
        self.user = config.get('user')
        self.password = config.get('password')
        self.dev = Device(self.host, port=self.port, user=self.user, password=self.password)

    def _do_open(self):
        try:
            self.dev.open()
            self.dev.bind(cu=Config)

        except ConnectAuthError as e:
            raise AuthenticationError

    def _do_close(self):
        self.dev.close()

    def _do_pull(self):
        options = {
            'format': 'text'
        }

        config = self.dev.rpc.get_config(filter_xml=None, options=options)
        config = config.text.encode('ascii', 'replace')
        return config

    def _do_push(self, fname, **kwargs):
        try:
            self.dev.cu.load(path=fname, format='text')

        # bogus exception on warnings
        except ConfigLoadError as e:
            # skip warnings
            if not e.errs['severity']:
                pass

    def _do_diff(self, index=0):
        return self.dev.cu.diff(index)

    def _do_lock(self):
        self.dev.cu.lock()

    def _do_unlock(self):
        self.dev.cu.unlock()

    def _do_commit(self, **kwargs):
        self.dev.cu.commit()

    def _do_check(self):
        self.dev.cu.commit_check()

    def _do_rollback(self, index=0):
        self.dev.cu.rollback(index)

