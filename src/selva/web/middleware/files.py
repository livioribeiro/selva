from pathlib import Path
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_file

from selva.configuration import Settings
from selva.di import Inject
from selva.web.middleware import CallNext, Middleware
from selva.web.exception import HTTPNotFoundException


class StaticFilesMiddleware(Middleware):
    settings: Annotated[Settings, Inject]

    def initialize(self):
        self.path = self.settings.staticfiles.path
        self.root = Path(self.settings.staticfiles.root).resolve()
        self.mappings = {
            name.lstrip("/"): value.lstrip("/") for name, value in
            self.settings.staticfiles.get("mappings").items()
        }

    async def __call__(
        self,
        call_next: CallNext,
        request: Request,
    ):
        file_to_serve = self.mappings.get(request.path.lstrip("/"))

        if not file_to_serve:
            if not request.path.startswith(self.path):
                await call_next(request)
                return

            file_to_serve = request.path.removeprefix(self.path)

        file_to_serve = file_to_serve.lstrip("/")
        path_to_serve = (self.root / file_to_serve).resolve()
        if not path_to_serve.is_relative_to(self.root) or not path_to_serve.exists() or not path_to_serve.is_file():
            raise HTTPNotFoundException()

        await respond_file(request.response, path_to_serve)


class UploadedFilesMiddleware(Middleware):
    settings: Annotated[Settings, Inject]

    def initialize(self):
        self.path = self.settings.uploadedfiles.path
        self.root = Path(self.settings.uploadedfiles.root).resolve()

    async def __call__(
        self,
        call_next: CallNext,
        request: Request,
    ):
        if not request.path.startswith(self.path):
            await call_next(request)
            return

        file_to_serve = request.path.removeprefix(self.path).lstrip("/")
        path_to_serve = (self.root / file_to_serve).resolve()
        if not path_to_serve.is_relative_to(self.root) or not path_to_serve.exists() or not path_to_serve.is_file():
            raise HTTPNotFoundException()

        await respond_file(request.response, path_to_serve)
