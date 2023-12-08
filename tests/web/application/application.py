from asgikit.responses import respond_text
from selva.web import controller, get


@controller
class Controller:
    @get
    async def index(self, request):
        await respond_text(request.response, "Selva")
