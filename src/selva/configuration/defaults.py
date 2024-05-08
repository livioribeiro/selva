default_settings = {
    "application": "application",
    "debug": False,
    "extensions": [],
    "middleware": [],
    "logging": {
        "setup": "selva.logging.setup",
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
