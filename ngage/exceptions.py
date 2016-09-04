
class ConnectionError(IOError):
    pass


class AuthenticationError(ConnectionError):
    pass


class ConfigError(ValueError):
    pass
