from asgikit.responses import respond_text

from selva.web import get


@get
async def index(request):
    await respond_text(request.response, "Ok")
