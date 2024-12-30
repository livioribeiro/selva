import functools
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_file

from selva.configuration import Settings
from selva.di.inject import Inject
from selva.web.middleware import CallNext
from selva.web.exception import HTTPNotFoundException


@functools.cache
def _static_files_middleware(settings: Settings) -> Callable[[CallNext, Request], Awaitable]:
    staticfiles_settings = settings.get("staticfiles")

    path = staticfiles_settings.path.lstrip("/")
    root = Path(staticfiles_settings.root).resolve()

    mappings = {
        name.lstrip("/"): value.lstrip("/")
        for name, value in staticfiles_settings.get("mappings", {}).items()
    }

    def get_file_to_serve(request: Request) -> str | None:
        request_path = request.path.lstrip("/")

        if file_to_serve := mappings.get(request_path):
            return file_to_serve.lstrip("/")

        if request_path.startswith(path):
            return request_path.removeprefix(path).lstrip("/")

        return None

    async def middleware(callnext: CallNext, request: Request):
        await _base_files_middleware(callnext, request, root, get_file_to_serve)

    return middleware


async def static_files_middleware(callnext: CallNext, request: Request, settings: Annotated[Settings, Inject]):
    await _static_files_middleware(settings)(callnext, request)


@functools.cache
def _uploaded_files_middleware(settings: Settings) -> Callable[[CallNext, Request], Awaitable]:
    uploadedfiles_settings = settings.get("uploadedfiles")

    path = uploadedfiles_settings.path.lstrip("/")
    root = Path(uploadedfiles_settings.root).resolve()

    def get_file_to_serve(request: Request) -> str | None:
        request_path = request.path.lstrip("/")

        if request_path.startswith(path):
            return request_path.removeprefix(path).lstrip("/")

        return None

    async def middleware(callnext: CallNext, request: Request):
        await _base_files_middleware(callnext, request, root, get_file_to_serve)

    return middleware


async def uploaded_files_middleware(callnext: CallNext, request: Request, settings: Annotated[Settings, Inject]):
    await _uploaded_files_middleware(settings)(callnext, request)


async def _base_files_middleware(call_next: CallNext, request: Request, root: Path, get_file_to_serve):
    if file_to_serve := get_file_to_serve(request):
        file_to_serve = (root / file_to_serve).resolve()
        if not (
            file_to_serve.is_file() and file_to_serve.is_relative_to(root)
        ):
            raise HTTPNotFoundException()

        await respond_file(request.response, file_to_serve)
    else:
        await call_next(request)
