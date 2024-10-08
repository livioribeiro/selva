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
    "staticfiles": {
        "path": "/static",
        "root": "resources/static",
        "mappings": {},
    },
    "uploadedfiles": {
        "path": "/uploads",
        "root": "resources/uploads",
    },
}
