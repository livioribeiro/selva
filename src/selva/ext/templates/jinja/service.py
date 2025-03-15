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

    async def render(
        self,
        template_name: str,
        context: dict,
    ):
        template = self.environment.get_template(template_name)
        return await template.render_async(context)

    # pylint: disable=too-many-arguments
    async def response(
        self,
        template_name: str,
        context: dict,
        *,
        status_code=HTTPStatus.OK,
        headers: dict = None,
        media_type="text/html",
        stream: bool = False,
    ) -> Response:
        media_type = media_type or "text/html"
        headers = headers or {}

        template = self.environment.get_template(template_name)

        if stream:
            render_stream = template.generate_async(context)
            response = StreamingResponse(
                render_stream,
                status_code=status_code,
                media_type=media_type,
                headers=headers,
            )
        else:
            rendered = await template.render_async(context)
            response = HTMLResponse(
                rendered,
                status_code=status_code,
                media_type=media_type,
                headers=headers,
            )

        return response

    async def respond(
        self,
        request: Request,
        template_name: str,
        context: dict,
        *,
        status_code=HTTPStatus.OK,
        headers: dict = None,
        media_type="text/html",
        stream: bool = False,
    ):
        response = await self.response(
            template_name,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            stream=stream,
        )

        await request.respond(response)
