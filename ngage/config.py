
import munge


class Config(munge.Config):
    defaults={
        'config': {
            'ngage': {
                'default': {
                    'user': None,
                    'password': None,
                    'port': None,
                    'type': 'eznc',
                    'driver_args': {},
                    },
                'plugin_path': [],
                'hosts': [],
                'groups': [],
                },
            'hosts': [],
            },
        'config_dir': None,
        'codec': 'yaml',
        }

