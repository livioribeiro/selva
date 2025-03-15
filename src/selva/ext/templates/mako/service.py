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
        status_code=HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        media_type="text/html",
    ) -> Response:
        media_type = media_type or "text/html"
        headers = headers or {}

        template = self.lookup.get_template(template_name)
        rendered = template.render(**context)
        return HTMLResponse(
            rendered, status_code=status_code, headers=headers, media_type=media_type
        )

    async def respond(
        self,
        request: Request,
        template_name: str,
        context: dict,
        *,
        status_code=HTTPStatus.OK,
        headers: dict[str, str] | None = None,
        media_type="text/html",
    ):
        response = self.response(
            template_name,
            context,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
        )
        await request.respond(response)
