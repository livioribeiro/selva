from pathlib import Path

from asgikit.responses import respond_text

from selva.web import get


@get("list")
async def index(request):
    uploads = Path("resources/uploads")
    files = [item.relative_to(uploads) for item in uploads.iterdir() if item.is_file()]
    result = "\n".join(f'<li><a href="/uploads/{item}">{item}</a></li>' for item in files)
    result = f"<html><body><ul>{result}</ul></body></html>"
    request.response.content_type = "text/html"
    await respond_text(request.response, result)
