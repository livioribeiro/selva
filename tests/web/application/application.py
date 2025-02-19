from selva.web import Request, get


@get
async def index(request: Request):
    await request.respond("Ok")
