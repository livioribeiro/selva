from selva.web.application import Application

from examples.modules import module_b, module_a

app = Application()
app.modules(module_a, module_b)

