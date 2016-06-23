
import inspect
import logging


class PluginBase(object):
    def __init__(self, config):
        super(PluginBase, self).__init__()
        self.config = config
        self.log = logging.getLogger('ngage.plugins.' + self.plugin_type)
        self.init()

    def init(self):
        pass


class DriverPlugin(PluginBase):
    def __init__(self, config):
        super(DriverPlugin, self).__init__(config)

        # base config options
        self.strict = self.config.get('strict', True)

    def _try_func(self, **kwargs):
        """ tries to call an internal method, fails based on strict config """
        try:
            func = inspect.currentframe().f_back.f_code.co_name
            call = "_do_" + func

            if not hasattr(self, call):
                raise TypeError("function '%s' not on object type %s"
                                % (call, self.plugin_type))

            self.log.debug(func)
            return getattr(self, call)(**kwargs)
        except NotImplementedError:
            if self.strict:
                raise

    def init(self):
        return self._try_func()

# public interface ###############################

    def open(self, **kwargs):
        'open connection to device'
        return self._try_func(**kwargs)

    def close(self, **kwargs):
        'close connection to device'
        return self._try_func(**kwargs)

    def lock(self):
        'lock config for exclusive access'
        rv = self._try_func()
        self.locked = True
        return rv

    def unlock(self):
        'unlock config'
        rv = self._try_func()
        self.locked = False
        return rv

    def pull(self):
        """ pull config from device """
        return self._try_func()

    def push(self, fname, **kwargs):
        """ push config from device """
        self.log.debug("push %s...", fname)
        self._do_push(fname, **kwargs)

    def diff(self, **kwargs):
        return self._try_func(**kwargs)

    def check(self, **kwargs):
        return self._try_func(**kwargs)

    def commit(self, **kwargs):
        return self._try_func(**kwargs)

    def rollback(self, **kwargs):
        return self._try_func(**kwargs)

# internal interface #############################

    def _do_init(self):
        pass

    def _do_open(self, **kwargs):
        raise NotImplementedError

    def _do_close(self, **kwargs):
        raise NotImplementedError

    def _do_lock(self):
        raise NotImplementedError

    def _do_unlock(self):
        raise NotImplementedError

    def _do_pull(self):
        """ internal method to pull a config file from a device """
        raise NotImplementedError

    def _do_push(self, fname, **kwawgs):
        """ internal method to push a single config file to a device """
        raise NotImplementedError

    def _do_diff(self, index=0):
        raise NotImplementedError

    def _do_check(self):
        raise NotImplementedError

    def _do_commit(self):
        raise NotImplementedError

    def _do_rollback(self, index=0):
        raise NotImplementedError

