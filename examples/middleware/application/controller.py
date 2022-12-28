from http import HTTPStatus

from selva.di import Inject
from selva.web import controller, get
from selva.web.request import Request
from selva.web.response import Response

from .auth import User
from .service import Greeter


@controller
class Controller:
    greeter: Greeter = Inject()

    @get
    async def index(self, context: Request):
        name = context.query.get("name")
        return {"message": self.greeter.greet(name)}

    @get("/protected")
    def protected(self, user: User):
        return {"message": f"Access granted to: {user.name}"}

    @get("/logout")
    def logout(self):
        return Response(
            status_code=HTTPStatus.UNAUTHORIZED,
            headers={"WWW-Authenticate": 'Basic realm="localhost:8000"'},
        )
