from selva.web import Application

from . import chat


app = Application()
app.register(chat)
