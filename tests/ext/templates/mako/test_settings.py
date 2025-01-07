from selva.ext.templates.mako.settings import MakoTemplateSettings


def modulename_callable():
    pass


def module_writer():
    pass


def preprocessor():
    pass


def include_error_handler():
    pass


class LexerCls:
    pass


cache_args = {
    "type": "file",
    "dir": "/tmp/cache",
}


def test_settings():
    settings = MakoTemplateSettings.model_validate(
        {
            "modulename_callable": f"{modulename_callable.__module__}:{modulename_callable.__qualname__}",
            "module_writer": f"{module_writer.__module__}:{module_writer.__qualname__}",
            "preprocessor": f"{preprocessor.__module__}:{preprocessor.__qualname__}",
            "include_error_handler": f"{include_error_handler.__module__}:{include_error_handler.__qualname__}",
            "lexer_cls": f"{LexerCls.__module__}:{LexerCls.__name__}",
            "cache_args": f"{test_settings.__module__}:cache_args",
        },
    )

    assert settings.modulename_callable is modulename_callable
    assert settings.module_writer is module_writer
    assert settings.preprocessor is preprocessor
    assert settings.include_error_handler is include_error_handler
    assert settings.lexer_cls is LexerCls
    assert settings.cache_args is cache_args
