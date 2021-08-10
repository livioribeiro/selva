from dependency_injector import Container

c = Container()


@c.transient
class Service1:
    pass


def test_call_function():
    def caller(service1: Service1):
        pass

    c.call(caller)


def test_call_function_args():
    def caller(service1: Service1, a: int):
        pass

    c.call(caller, kwargs={"a": 1})
