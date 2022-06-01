from asgikit.responses import JsonResponse

from selva.web import controller, get


@controller("/reverse")
class Controller:
    @get("{name}")
    def index(self, name: str) -> JsonResponse:
        return JsonResponse({"original": name, "reversed": "".join(reversed(name))})
