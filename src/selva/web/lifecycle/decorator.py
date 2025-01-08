ATTRIBUTE_STARTUP = "__selva_startup__"
ATTRIBUTE_BACKGROUND = "__selva_background__"


def startup(target):
    setattr(target, ATTRIBUTE_STARTUP, True)
    return target


def background(target):
    setattr(target, ATTRIBUTE_BACKGROUND, True)
    return target
