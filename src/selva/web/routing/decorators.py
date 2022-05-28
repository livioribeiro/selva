from enum import Enum

from asgikit.requests import HttpMethod

from selva.di.decorators import transient

CONTROLLER_ATTRIBUTE = "__selva_web_controller__"
ACTION_ATTRIBUTE = "__selva_web_action__"
PATH_ATTRIBUTE = "__selva_web_path__"


class ActionType(Enum):
    GET = HttpMethod.GET
    POST = HttpMethod.POST
    PUT = HttpMethod.PUT
    PATCH = HttpMethod.PATCH
    DELETE = HttpMethod.DELETE
    WEBSOCKET = "WEBSOCKET"


def controller(path: str):
    if path and not isinstance(path, str):
        raise ValueError(f"Invalid argument for @controller: {path}")

    def inner(controller_class: type):
        setattr(controller_class, CONTROLLER_ATTRIBUTE, True)
        setattr(controller_class, PATH_ATTRIBUTE, path)
        return transient(controller_class)

    return inner


def route(method: HttpMethod, path: str):
    def inner(action):
        setattr(action, ACTION_ATTRIBUTE, ActionType(method))
        setattr(action, PATH_ATTRIBUTE, path)
        return action

    return inner


def websocket(path: str):
    def inner(action):
        setattr(action, ACTION_ATTRIBUTE, ActionType.WEBSOCKET)
        setattr(action, PATH_ATTRIBUTE, path)
        return action

    return inner


def get(path: str):
    return route(HttpMethod.GET, path)


def post(path: str):
    return route(HttpMethod.POST, path)


def put(path: str):
    return route(HttpMethod.PUT, path)


def patch(path: str):
    return route(HttpMethod.PATCH, path)


def delete(path: str):
    return route(HttpMethod.DELETE, path)
