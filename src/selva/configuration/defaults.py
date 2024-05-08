default_settings = {
    "application": "application",
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
