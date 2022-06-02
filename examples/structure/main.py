from selva.web.application import Application

from . import modules

app = Application()
app.register(modules)

