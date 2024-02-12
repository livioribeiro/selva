default_settings = {
    "application": "application",
    "extensions": [],
    "middleware": [],
    "logging": {
        "setup": "selva.logging.setup.setup_logger",
        "root": "WARNING",
        "level": {},
        "enable": [],
        "disable": [],
    },
    "templates": {
        "backend": None,
        "paths": ["resources/templates"],
        "jinja": {},
    },
    "data": {
        "redis": {},
        "sqlalchemy": {},
    },
}
