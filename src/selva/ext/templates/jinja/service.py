from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from jinja2 import Environment, FileSystemLoader

from selva.conf import Settings
from selva.di import Inject, service
from selva.ext.templates.jinja.settings import JinjaTemplateSettings
from selva.web import Response, HTMLResponse, StreamingResponse


@service
class JinjaTemplate:
    settings: Annotated[Settings, Inject]
    environment: Environment

    def initialize(self):
        jinja_settings = JinjaTemplateSettings.model_validate(
            self.settings.templates.jinja
        )

        kwargs = jinja_settings.model_dump(exclude_none=True)

        if "loader" not in kwargs:
            paths = kwargs.pop("paths")
            templates_path = [Path(p).absolute() for p in paths]
            kwargs["loader"] = FileSystemLoader(templates_path)

        self.environment = Environment(enable_async=True, **kwargs)

    # pylint: disable=too-many-arguments
    async def response(
        self,
        template_name: str,
        context: dict,
        *,
        status=HTTPStatus.OK,
        headers=None,
        content_type="text/html",
        stream: bool = False,
    ) -> Response:
        content_type = content_type or "text/html"
        headers = headers or {}

        template = self.environment.get_template(template_name)

        if stream:
            render_stream = template.generate_async(context)
            response = StreamingResponse(
                render_stream,
                status_code=status,
                media_type=content_type,
                headers=headers,
            )
        else:
            rendered = await template.render_async(context)
            response = HTMLResponse(
                rendered, status_code=status, media_type=content_type, headers=headers
            )

        return response

    async def render(self, template_name: str, context: dict) -> str:
        template = self.environment.get_template(template_name)
        return await template.render_async(context)

    async def render_str(self, source: str, context: dict) -> str:
        template = self.environment.from_string(source)
        return await template.render_async(context)
