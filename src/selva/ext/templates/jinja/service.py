from collections.abc import Callable, Iterable
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from selva.conf import Settings
from selva.di.decorator import service
from selva.ext.templates.jinja.settings import JinjaTemplateSettings


def jinja_environment(settings: Settings) -> Environment:
    jinja_settings = JinjaTemplateSettings.model_validate(
        settings.templates.jinja
    )

    kwargs = jinja_settings.model_dump(exclude_none=True)

    if "loader" not in kwargs:
        paths = kwargs.pop("paths")
        templates_path = [Path(p).absolute() for p in paths]
        kwargs["loader"] = FileSystemLoader(templates_path)

    return Environment(enable_async=True, **kwargs)


def get_template_services(environment: Environment) -> Iterable[Callable[[Environment], Template]]:
    for tpl in environment.loader.list_templates():
        @service(name=tpl)
        def template_service(inner_environ: Environment) -> Template:
            return inner_environ.get_template(tpl)

        yield template_service
