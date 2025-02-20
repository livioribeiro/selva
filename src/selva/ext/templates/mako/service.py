import asyncio
from http import HTTPStatus
from typing import Annotated

from mako.lookup import TemplateLookup

from selva.conf import Settings
from selva.di import Inject, service
from selva.ext.templates.mako.settings import MakoTemplateSettings
from selva.web import Response, HTMLResponse


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
    async def response(
        self,
        template_name: str,
        context: dict,
        *,
        status=HTTPStatus.OK,
        headers=None,
        content_type="text/html",
    ) -> Response:
        content_type = content_type or "text/html"
        headers = headers or {}

        template = self.lookup.get_template(template_name)
        rendered = await asyncio.to_thread(template.render, **context)
        return HTMLResponse(
            rendered, status=status, headers=headers, content_type=content_type
        )

    async def render(self, template_name: str, context: dict) -> str:
        template = self.lookup.get_template(template_name)
        return template.render(**context)

    async def render_str(self, source: str, context: dict) -> str:
        template_hash = str(hash(source))
        if not self.lookup.has_template(template_hash):
            self.lookup.put_string(template_hash, source)

        template = self.lookup.get_template(template_hash)
        return template.render(**context)
