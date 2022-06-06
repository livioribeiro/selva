from asgikit.requests import HttpRequest
from asgikit.responses import JsonResponse

from examples.database import modules
from selva.web import Application, controller, get


@controller("/")
class IndexController:
    @get
    def index(self, request: HttpRequest):
        host = request.headers.get_first("host")
        base_url = f"http://{host}"

        return JsonResponse(
            {
                "sqlite+databases": f"{base_url}/sqlite",
                "postgres+asyncpg": f"{base_url}/postgres",
            }
        )


app = Application()
app.register(IndexController, modules)
