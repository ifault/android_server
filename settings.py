TORTOISE_ORM = {
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
    'apps': {
        'models': {
            'models': ['models'],
            'default_connection': 'default',
        }
    },
    'connections': {
        'default': 'sqlite://db.sqlite3',
    }
}
