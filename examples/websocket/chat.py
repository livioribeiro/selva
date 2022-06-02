from selva.web import Application

from . import chat_module


app = Application()
app.modules(chat_module)
