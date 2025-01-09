from typing import Annotated

from asgikit.responses import Response, respond_text
from mako.lookup import TemplateLookup

from selva.configuration import Settings
from selva.di import Inject, service
from selva.ext.templates.mako.settings import MakoTemplateSettings


@service
class MakoTemplate:
    settings: Annotated[Settings, Inject]

    lookup: TemplateLookup = None

    def initialize(self):
        mako_settings = MakoTemplateSettings.model_validate(
            self.settings.templates.mako
        )

        kwargs = mako_settings.model_dump(exclude_none=True)
        self.lookup = TemplateLookup(**kwargs)

    # pylint: disable=too-many-arguments
    async def respond(
        self,
        response: Response,
        template_name: str,
        context: dict,
        *,
        content_type: str | None = None,
    ):
        if content_type:
            response.content_type = content_type
        elif not response.content_type:
            response.content_type = "text/html"

        template = self.lookup.get_template(template_name)
        rendered = template.render(**context)
        await respond_text(response, rendered)

    async def render(self, template_name: str, context: dict) -> str:
        template = self.lookup.get_template(template_name)
        return template.render(**context)

    async def render_str(self, source: str, context: dict) -> str:
        template_hash = str(hash(source))
        if not self.lookup.has_template(template_hash):
            self.lookup.put_string(template_hash, source)

        template = self.lookup.get_template(template_hash)
        return template.render(**context)
