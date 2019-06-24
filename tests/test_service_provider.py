from typing import cast, ForwardRef

import pytest

from simpleinject.service_provider import ServicesManager, CircularReferenceError, ServiceWasNotRegistered


@pytest.fixture('function')
def services_manager():
    return ServicesManager()


class ServiceB(object):
    pass


class ServiceC(object):
    pass


class ServiceA(object):
    def __init__(self, b: ServiceB, c: ServiceC):
        self.b: ServiceB = b
        self.c: ServiceC = c


def test_injection_self(services_manager: ServicesManager):
    services_manager.bind(ServiceB, ServiceB)
    services_manager.bind(ServiceC, ServiceC)
    services_manager.bind(ServiceA, ServiceA)

    services_manager.init_dependencies()
    services_manager.resolve_graph()

    a: ServiceA = cast(ServiceA, services_manager.services[ServiceA].instance)
    b: ServiceB = cast(ServiceB, services_manager.services[ServiceB].instance)
    c: ServiceC = cast(ServiceC, services_manager.services[ServiceC].instance)

    assert a and b and c
    assert id(b) == id(a.b)
    assert id(c) == id(a.c)


class IService(object):
    def __init__(self):
        pass


class ServiceD(IService):
    def __init__(self):
        super().__init__()


def test_register_service_to_interface(services_manager: ServicesManager):
    services_manager.bind(IService, ServiceD)

    services_manager.init_dependencies()
    services_manager.resolve_graph()

    service = services_manager.services[IService].instance

    assert type(service) == ServiceD


class ServiceE(object):
    def __init__(self, f: ForwardRef("ServiceF")):
        pass


class ServiceF(object):
    def __init__(self, e: ServiceE):
        pass


def test_circular_dependency(services_manager: ServicesManager):
    services_manager.bind_self(ServiceE)
    services_manager.bind_self(ServiceF)

    services_manager.init_dependencies()

    with pytest.raises(CircularReferenceError):
        services_manager.resolve_graph()


class ServiceG(object):
    def __init__(self):
        self.value: int = 1


def test_bind_self(services_manager: ServicesManager):
    services_manager.bind_self(ServiceG)

    services_manager.init_dependencies()
    services_manager.resolve_graph()

    service: ServiceG = cast(ServiceG, services_manager.services[ServiceG].instance)

    assert 1 == service.value


def test_retrieve_from_concrete_type(services_manager: ServicesManager):
    services_manager.bind_self(ServiceG)

    services_manager.init_dependencies()
    services_manager.resolve_graph()

    service: ServiceG = cast(ServiceG, services_manager.resolve(ServiceG))

    assert 1 == service.value


class IServiceH(object):
    pass


class ServiceH(IServiceH):
    def __init__(self):
        self.value: int = 1


def test_retrieve_from_interface_type(services_manager: ServicesManager):
    services_manager.bind(IServiceH, ServiceH)

    services_manager.init_dependencies()
    services_manager.resolve_graph()

    service: ServiceH = cast(ServiceH, services_manager.resolve(IServiceH))

    assert 1 == service.value


def test_service_not_register(services_manager: ServicesManager):
    services_manager.bind(IServiceH, ServiceH)

    services_manager.init_dependencies()
    services_manager.resolve_graph()
    with pytest.raises(ServiceWasNotRegistered):
        services_manager.resolve(ServiceH)
