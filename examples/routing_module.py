from selva.web.application import Application

from . import controllers

app = Application()
app.modules(controllers)

