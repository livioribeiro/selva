from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_file

from selva.configuration import Settings
from selva.di.inject import Inject
from selva.web.middleware import CallNext
from selva.web.exception import HTTPNotFoundException


_static_files_middleware = None
async def static_files_middleware(callnext, request, settings: Annotated[Settings, Inject]):
    global _static_files_middleware

    if not _static_files_middleware:
        settings = settings.get("staticfiles")

        path = settings.path.lstrip("/")
        root = Path(settings.root).resolve()

        mappings = {
            name.lstrip("/"): value.lstrip("/")
            for name, value in settings.get("mappings", {}).items()
        }

        _static_files_middleware = StaticFilesMiddleware(path, root, mappings)

    await _static_files_middleware(callnext, request)


_uploaded_files_middleware = None
async def uploaded_files_middleware(callnext, request, settings: Annotated[Settings, Inject]):
    global _uploaded_files_middleware

    if not _uploaded_files_middleware:
        settings = settings.get("uploadedfiles")

        path = settings.path.lstrip("/")
        root = Path(settings.root).resolve()

        _uploaded_files_middleware = UploadedFilesMiddleware(path, root)

    await _uploaded_files_middleware(callnext, request)


class BaseFilesMiddleware(metaclass=ABCMeta):
    def __init__(self, path: str, root: Path):
        self.path = path
        self.root = root

    @abstractmethod
    def get_file_to_serve(self, request: Request) -> str | None:
        pass

    async def __call__(self, call_next: CallNext, request: Request):
        if file_to_serve := self.get_file_to_serve(request):
            file_to_serve = (self.root / file_to_serve).resolve()
            if not (
                file_to_serve.is_file() and file_to_serve.is_relative_to(self.root)
            ):
                raise HTTPNotFoundException()

            await respond_file(request.response, file_to_serve)
        else:
            await call_next(request)


class StaticFilesMiddleware(BaseFilesMiddleware):
    def __init__(self, path: str, root: Path, mappings: dict[str, str]):
        super().__init__(path, root)
        self.mappings = mappings

    def get_file_to_serve(self, request: Request) -> str | None:
        request_path = request.path.lstrip("/")

        if file_to_serve := self.mappings.get(request_path):
            return file_to_serve.lstrip("/")

        if request_path.startswith(self.path):
            return request_path.removeprefix(self.path).lstrip("/")

        return None


class UploadedFilesMiddleware(BaseFilesMiddleware):
    def get_file_to_serve(self, request: Request) -> str | None:
        request_path = request.path.lstrip("/")

        if request_path.startswith(self.path):
            return request_path.removeprefix(self.path).lstrip("/")

        return None
