import asyncio
import mimetypes
import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from email.utils import formatdate
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
        self,
        app,
        path: str,
        root: Path,
        filelist: dict[str, tuple[str, int, str]],
        mappings: dict[str, str],
    ):
        super().__init__(app, path, root)
        self.filelist = filelist
        self.mappings = mappings

    def get_file_to_serve(self, scope: dict) -> str | None:
        request_path = scope["path"].lstrip("/")

        file_to_serve = None
        if file_path := self.mappings.get(request_path):
            file_to_serve = file_path
        elif request_path.startswith(self.path):
            file_path = os.path.join(self.root, request_path.removeprefix(self.path))
            if file_path in self.filelist:
                file_to_serve = file_path

        if file_to_serve:
            file_data = self.filelist[file_to_serve]
            content_type, content_length, last_modified = file_data

            # use Request to set response headers
            request = Request(scope, None, None)
            request.response.content_type = content_type
            request.response.content_length = content_length
            request.response.header("last-modified", last_modified)

            return file_to_serve

        return None

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except HTTPNotFoundException:
            if scope["path"] == "/":
                new_scope = scope | {"path": f"{self.path}/index.html"}
                await super().__call__(new_scope, receive, send)
            else:
                raise


async def static_files_middleware(app, settings: Settings, di: Container):
    settings = settings.staticfiles
    path = settings.path.lstrip("/")
    root = Path(settings.root).resolve().absolute()

    # dict of file path to (content-type, content-length, last-modified)
    filelist: dict[str, tuple[str, int, str]] = {}

    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            file = os.path.join(dirpath, filename)
            stat = await asyncio.to_thread(os.stat, file)

            m_type, _ = mimetypes.guess_type(filename, strict=False)
            m_type = m_type or "application/octet-stream"
            last_modified = formatdate(stat.st_mtime, usegmt=True)

            filelist[os.path.join(dirpath, filename)] = (
                m_type,
                stat.st_size,
                last_modified,
            )

    mappings = {
        name.lstrip("/"): os.path.join(root, value.lstrip("/"))
        for name, value in settings.get("mappings", {}).items()
    }

    if difference := set(mappings.values()).difference(filelist):
        files = ", ".join(difference)
        raise ValueError(f"Static files mappings not found: {files}")

    return StaticFilesMiddleware(app, path, root, filelist, mappings)


def uploaded_files_middleware(app, settings: Settings, di: Container):
    settings = settings.uploadedfiles
    path = settings.path.lstrip("/")
    root = Path(settings.root).resolve()
    return UploadedFilesMiddleware(app, path, root)
