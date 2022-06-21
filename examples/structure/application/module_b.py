from selva.web import controller, get


@controller("/reverse")
class Controller:
    @get("{name}")
    def index(self, name: str):
        return {"original": name, "reversed": "".join(reversed(name))}
