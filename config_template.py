mongo = {
    'host': '127.0.0.1',
    'port': '27017',
    'user': 'test_user',
    'passwd': 'resu_tset',
    'authdb': 'test_db',
    'db': 'test_db',
    'collection': 'test_collection',
}

email = {
    'error_from': 'Archiver Errors <noreply@jax.org>',
    'error_to': 'Archive-Team@jax.org',
    'error_subject': 'Archive error',
    'error_recipients': ['frank.zappulla@jax.org', 'mitch.kostich@jax.org'],
    'error_return': 'noreply@jax.org',
    'smtp_host': 'smtp.jax.org',
    'smpt_port': 25,
}

api_keys = {
    'abc123': {
        'userid': 'kostim',
        'firstname': 'mitch',
        'lastname': 'kostich',
        'email': 'mitch.kostich@jax.org',
        'admin': False,
    },
    '123abc': {
        'userid': 'kostim',
        'firstname': 'mitch',
        'lastname': 'kostich',
        'email': 'mitch.kostich@jax.org',
        'admin': True,
    },
}

time = {
    'format_sec': '%Y-%m-%d %H:%M:%S %Z%z',
    'format_day': '%Y-%m-%d',
    'zone': 'US/Eastern',
}

testing = {
    'email_on': True,
    'mongo_on': True,
    'pbs_on': True,
}

