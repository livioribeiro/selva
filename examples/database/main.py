from selva.web import Application

from . import sqlite_database

app = Application()
app.register(sqlite_database)
