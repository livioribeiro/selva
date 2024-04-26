default_settings = {
    "application": "application",
    "extensions": [],
    "middleware": [],
    "logging": {
        "setup": "selva.logging.setup.setup_logging",
        "config": {
            "handlers": [
                {
                    "sink": "ext://sys.stderr",
                    "level": "INFO",
                    "diagnose": True,
                    "backtrace": False,
                },
            ]
        },
    },
    "templates": {
        "backend": None,
        "paths": ["resources/templates"],
        "jinja": {},
    },
    "data": {
        "memcached": {},
        "redis": {},
        "sqlalchemy": {},
    },
}
