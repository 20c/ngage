import ipaddress

from pybird import PyBird

import ngage
from ngage.exceptions import AuthenticationError, ConfigError


@ngage.plugin.register("bird")
class Driver(ngage.plugins.DriverPlugin):
    plugin_type = "bird"

    def _do_init(self):
        config = self.config

        self.host = config.get("host")
        self.user = config.get("user")
        self.password = config.get("password")
        self.optional_args = config.get("driver_args", {})

        self.socket_file = self.optional_args.pop("socket_file", None)
        if not self.socket_file:
            raise ValueError("bird requires socket_file in driver_args")

        self.dev = PyBird(
            self.socket_file, self.host, self.user, self.password, **self.optional_args
        )

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
        return self.dev.get_config()

    def _do_push(self, fname, **kwargs):
        with open(fname) as fobj:
            conf = fobj.read()
        return self.dev.put_config(conf)

    def _do_diff(self, index=0):
        return
        if index != 0:
            raise NotImplementedError("version index not implemented")
        return self.dev.compare_config()

    def _do_lock(self):
        pass
        # self.dev.lock()

    def _do_unlock(self):
        pass
        # self.dev.unlock()

    def _do_commit(self, **kwargs):
        self.dev.commit_config()

    def _do_check(self):
        self.dev.check_config()

    def _do_rollback(self, index=0):
        if index == 0:
            self.dev.discard_config()
        elif index == 1:
            self.dev.rollback()
        else:
            raise NotImplementedError("version index not implemented")

    def _do_lookup_peer(self, peer):
        # may want to cache this?
        peers = self.dev.get_peer_status()

        if peer.lower().startswith("as"):
            for each in peers:
                if each["asn"] == peer[2:]:
                    return each["name"]

        for each in peers:
            if each["name"] == peer:
                return peer
            elif each["address"] == peer:
                return each["name"]
            elif each["asn"] == peer:
                return each["name"]

        raise ValueError(f"peer {peer} not found")

    def _do_get_bgp_neighbors(self):
        router_id = self.dev.get_bird_status().get("router_id", "")

        field_map = {
            # 'local_as'
            "asn": "remote_as",
            "router_id": "remote_id",
            "up": "is_up",
            "description": "description",
            # 'uptime'
        }

        rv = {
            "router_id": router_id,
            "peers": {},
        }

        for peer in self.dev.get_peer_status():
            if peer["protocol"] != "BGP":
                continue

            # TODO use inet abstraction
            addr = ipaddress.ip_address(str(peer["address"]))

            row = {v: peer.get(k, None) for k, v in list(field_map.items())}
            row["is_enabled"] = True
            row["address_family"] = {
                f"ipv{addr.version}": {
                    "received_prefixes": 0,
                    "accepted_prefixes": peer["routes_imported"],
                    "sent_prefixes": peer["routes_exported"],
                }
            }
            rv["peers"][addr] = row

        return rv

    def _do_get_routes(self, **kwargs):
        routes = self.dev.get_routes(**kwargs)
        return routes
