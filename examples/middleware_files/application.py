from asgikit.responses import respond_text
from selva.web import controller, get


@controller
class Controller:
    @get
    async def index(self, request):
        request.response.content_type = "text/html"
        await respond_text(request.response, "Lorem ipsum dolor sit amet")
