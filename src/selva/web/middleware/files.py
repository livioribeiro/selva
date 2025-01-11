import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path

import structlog
from asgikit.requests import Request
from asgikit.responses import respond_file

from selva.configuration import Settings
from selva.di import Container
from selva.web.exception import HTTPNotFoundException

logger = structlog.get_logger()


class BaseFilesMiddleware(ABC):
    def __init__(self, app: Callable, path: str, root: Path):
        self.app = app
        self.path = path if path.endswith("/") else path + "/"
        self.root = root

    @abstractmethod
    def get_file_to_serve(self, scope: dict) -> str | None:
        pass

    async def __call__(self, scope, receive, send):
        if file_to_serve := self.get_file_to_serve(scope):
            file_to_serve = (self.root / file_to_serve).resolve()
            if not (
                file_to_serve.is_file() and file_to_serve.is_relative_to(self.root)
            ):
                raise HTTPNotFoundException()

            request = Request(scope, receive, send)
            await respond_file(request.response, file_to_serve)
        else:
            await self.app(scope, receive, send)


class UploadedFilesMiddleware(BaseFilesMiddleware):
    def get_file_to_serve(self, scope: dict) -> str | None:
        request_path = scope["path"].lstrip("/")

        if request_path.startswith(self.path):
            return request_path.removeprefix(self.path).lstrip("/")

        return None


class StaticFilesMiddleware(BaseFilesMiddleware):
    def __init__(
        self, app, path: str, root: Path, filelist: set[str], mappings: dict[str, str]
    ):
        super().__init__(app, path, root)
        self.filelist = filelist
        self.mappings = mappings

    def get_file_to_serve(self, scope: dict) -> str | None:
        request_path = scope["path"].lstrip("/")

        if file := self.mappings.get(request_path):
            return file

        if request_path.startswith(self.path):
            filename = request_path.removeprefix(self.path)
            file = os.path.join(self.root, filename)
            if file in self.filelist:
                return file

        return None

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except HTTPNotFoundException:
            index_html = self.root / "index.html"
            if scope["path"].lstrip("/") == "" and index_html.exists():
                request = Request(scope, receive, send)
                await respond_file(request.response, index_html)
            else:
                raise


def static_files_middleware(app, settings: Settings, di: Container):
    settings = settings.staticfiles
    path = settings.path.lstrip("/")
    root = Path(settings.root).resolve().absolute()

    filelist = set()
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            filelist.add(os.path.join(dirpath, filename))

    mappings = {
        name.lstrip("/"): os.path.join(root, value.lstrip("/"))
        for name, value in settings.get("mappings", {}).items()
    }

    if difference := set(mappings.values()).difference(filelist):
        files = ", ".join(difference)
        raise ValueError(f"Static files mappings not found: {files}")

    return StaticFilesMiddleware(app, path, root, filelist, mappings)


def uploaded_files_middleware(app, settings: Settings, di: Container):
    settings = settings.staticfiles
    path = settings.path.lstrip("/")
    root = Path(settings.root).resolve()
    return UploadedFilesMiddleware(app, path, root)
