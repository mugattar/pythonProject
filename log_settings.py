log_config = {
    'version': 1,
    'formatters': {
        'stream_formatter': {
            'format': '%(levelname)s %(message)s',
        },
        'file_formatter': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%d-%m-%Y %H:%M',
        },
    },
    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'stream_formatter',
            'level': 'INFO',
        },
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'file_formatter',
            'filename': 'bot.log',
            'level': 'DEBUG',
            'encoding': 'utf8'
        },
    },
    'loggers': {
        'bot': {
            'handlers': ['file_handler', 'stream_handler'],
            'level': 'DEBUG',
        },
    },
}
