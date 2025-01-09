from pathlib import Path
from typing import Annotated

from asgikit.responses import Response, respond_stream, respond_text
from jinja2 import Environment, FileSystemLoader

from selva.configuration import Settings
from selva.di import Inject, service
from selva.ext.templates.jinja.settings import JinjaTemplateSettings


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
    async def respond(
        self,
        response: Response,
        template_name: str,
        context: dict,
        *,
        content_type: str | None = None,
        stream: bool = False,
    ):
        if content_type:
            response.content_type = content_type
        elif not response.content_type:
            response.content_type = "text/html"

        template = self.environment.get_template(template_name)

        if stream:
            render_stream = template.generate_async(context)
            await respond_stream(response, render_stream)
        else:
            rendered = await template.render_async(context)
            await respond_text(response, rendered)

    async def render(self, template_name: str, context: dict) -> str:
        template = self.environment.get_template(template_name)
        return await template.render_async(context)

    async def render_str(self, source: str, context: dict) -> str:
        template = self.environment.from_string(source)
        return await template.render_async(context)
