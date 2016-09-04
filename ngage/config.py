
import munge


class Config(munge.Config):
    defaults={
        'config': {
            'ngage': {
                'type': None,
                'plugin_path': [],
                },
            'hosts': [],
            },
        'config_dir': None,
        'codec': 'yaml',
        }

