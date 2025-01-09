default_settings = {
    "application": "application",
    "extensions": [],
    "middleware": [],
    "logging": {
        "setup": "selva.logging:setup",
    },
    "templates": {
        "jinja": {},
        "mako": {},
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
