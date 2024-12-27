from pathlib import Path

from asgikit.responses import Response, respond_stream, respond_text
from jinja2 import Environment, FileSystemLoader, select_autoescape

from selva.configuration import Settings
from selva.di import service
from selva.ext.templates.jinja.settings import JinjaTemplateSettings
from selva.web.templates import Template


@service
async def jinja_template_service(locator) -> Template:
    settings = await locator.get(Settings)
    jinja_settings = JinjaTemplateSettings.model_validate(
        settings.templates.jinja
    )

    kwargs = jinja_settings.model_dump(exclude_unset=True)

    if "loader" not in kwargs:
        templates_path = [Path(p).absolute() for p in settings.templates.paths]
        kwargs["loader"] = FileSystemLoader(templates_path)

    if "autoescape" not in kwargs:
        kwargs["autoescape"] = select_autoescape()

    environment = Environment(enable_async=True, **kwargs)

    return JinjaTemplate(environment)


class JinjaTemplate(Template):
    def __init__(self, environment: Environment):
        self.environment = environment

    async def respond(
        self,
        response: Response,
        template_name: str,
        context: dict,
        *,
        content_type: str = None,
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
