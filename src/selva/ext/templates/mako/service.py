from http import HTTPStatus
from typing import Annotated

from mako.lookup import TemplateLookup

from selva.conf import Settings
from selva.di import Inject, service
from selva.ext.templates.mako.settings import MakoTemplateSettings
from selva.web import Request, Response, HTMLResponse


@service
def template_lookup(settings: Settings) -> TemplateLookup:
    mako_settings = MakoTemplateSettings.model_validate(settings.templates.mako)

    kwargs = mako_settings.model_dump(exclude_none=True)
    return TemplateLookup(**kwargs)


@service
class MakoTemplate:
    settings: Annotated[Settings, Inject]
    lookup: Annotated[TemplateLookup, Inject]

    # pylint: disable=too-many-arguments
    def response(
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
        rendered = template.render(**context)
        return HTMLResponse(
            rendered, status=status, headers=headers, content_type=content_type
        )

    async def respond(
        self,
        request: Request,
        template_name: str,
        context: dict,
        *,
        status=HTTPStatus.OK,
        headers=None,
        content_type="text/html",
    ):
        response = self.response(
            template_name,
            context,
            status=status,
            headers=headers,
            content_type=content_type,
        )
        await request.respond(response)
