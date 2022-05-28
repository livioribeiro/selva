from selva.web.application import Application

import controllers

app = Application()
app.modules(controllers)

