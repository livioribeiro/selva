from selva.web.application import Application

from . import crud_module

app = Application()
app.modules(crud_module)
