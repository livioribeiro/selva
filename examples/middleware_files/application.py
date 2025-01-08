from asgikit.responses import respond_text

from selva.web import get


@get
async def index(request):
    request.response.content_type = "text/html"
    await respond_text(request.response, "Lorem ipsum dolor sit amet")
