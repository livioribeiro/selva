class ExtensionNotFoundError(Exception):
    def __init__(self, name):
        super().__init__(f"Extension '{name}' not found")


class ExtensionMissingInitFunctionError(Exception):
    def __init__(self, name):
        super().__init__(
            f"Extension '{name}' is missing the 'init_extension()' function"
        )
