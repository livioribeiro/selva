from pathlib import Path

from selva.web import Request, HTMLResponse, get


@get("list")
async def index(request: Request):
    uploads = Path("resources/uploads")

    files = [item.relative_to(uploads) for item in uploads.iterdir() if item.is_file()]
    result = "\n".join(
        f'<li><a href="/uploads/{item}">{item}</a></li>' for item in files
    )
    result = f"<html><body><ul>{result}</ul></body></html>"

    response = HTMLResponse(result)
    await request.respond(response)
