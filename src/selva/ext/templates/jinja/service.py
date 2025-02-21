from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from jinja2 import Environment, FileSystemLoader

from selva.conf import Settings
from selva.di.decorator import service
from selva.di.inject import Inject
from selva.ext.templates.jinja.settings import JinjaTemplateSettings
from selva.web.http import Request, Response, HTMLResponse, StreamingResponse


@service
def jinja_environment(settings: Settings) -> Environment:
    jinja_settings = JinjaTemplateSettings.model_validate(settings.templates.jinja)

    kwargs = jinja_settings.model_dump(exclude_none=True)

    if "loader" not in kwargs:
        paths = kwargs.pop("paths")
        templates_path = [Path(p).absolute() for p in paths]
        kwargs["loader"] = FileSystemLoader(templates_path)

    return Environment(enable_async=True, **kwargs)


@service
class JinjaTemplate:
    settings: Annotated[Settings, Inject]
    environment: Annotated[Environment, Inject]

    # pylint: disable=too-many-arguments
    async def response(
        self,
        template_name: str,
        context: dict,
        *,
        status=HTTPStatus.OK,
        headers: dict = None,
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
                status=status,
                content_type=content_type,
                headers=headers,
            )
        else:
            rendered = await template.render_async(context)
            response = HTMLResponse(
                rendered, status=status, content_type=content_type, headers=headers
            )

        return response

    async def respond(
        self,
        request: Request,
        template_name: str,
        context: dict,
        *,
        status=HTTPStatus.OK,
        headers: dict = None,
        content_type="text/html",
        stream: bool = False,
    ):
        response = await self.response(
            template_name,
            context,
            status=status,
            headers=headers,
            content_type=content_type,
            stream=stream,
        )

        await request.respond(response)
