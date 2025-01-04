from abc import ABC, abstractmethod
from pathlib import Path
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_file

from selva.configuration import Settings
from selva.di.decorator import service
from selva.di.inject import Inject
from selva.web.exception import HTTPNotFoundException
from selva.web.middleware import CallNext


class BaseFilesMiddleware(ABC):
    settings: Annotated[Settings, Inject]

    settings_property: str
    path: str
    root: Path

    def initialize(self):
        settings = self.settings.get(self.settings_property)
        self.path = settings.path.lstrip("/")
        self.root = Path(settings.root).resolve()

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


@service
class UploadedFilesMiddleware(BaseFilesMiddleware):
    settings_property = "uploadedfiles"

    def get_file_to_serve(self, request: Request) -> str | None:
        request_path = request.path.lstrip("/")

        if request_path.startswith(self.path):
            return request_path.removeprefix(self.path).lstrip("/")

        return None


@service
class StaticFilesMiddleware(BaseFilesMiddleware):
    settings_property = "staticfiles"
    mappings: dict[str, str]

    def initialize(self):
        super().initialize()

        settings = self.settings.get(self.settings_property)

        # TODO: build a map of all files under the staticfiles root directory
        self.mappings = {
            name.lstrip("/"): value.lstrip("/")
            for name, value in settings.get("mappings", {}).items()
        }

    def get_file_to_serve(self, request: Request) -> str | None:
        request_path = request.path.lstrip("/")

        if file_to_serve := self.mappings.get(request_path):
            return file_to_serve.lstrip("/")

        if request_path.startswith(self.path):
            return request_path.removeprefix(self.path).lstrip("/")

        return None


async def static_files_middleware(
    callnext: CallNext,
    request: Request,
    middleware_service: Annotated[StaticFilesMiddleware, Inject],
):
    await middleware_service(callnext, request)


async def uploaded_files_middleware(
    callnext: CallNext,
    request: Request,
    middleware_service: Annotated[UploadedFilesMiddleware, Inject],
):
    await middleware_service(callnext, request)
