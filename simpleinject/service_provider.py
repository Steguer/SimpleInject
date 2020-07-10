import inspect
from typing import *


class ServiceWrapper(object):
    def __init__(self, service_type: type, instance: object = None):
        self.service_type = service_type
        self.instance: object = instance
        self.dependencies: List[ServiceWrapper] = []


class Dummy(object):
    pass


class CircularReferenceError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ServiceWasNotRegistered(Exception):
    def __init__(self, service: Type):
        super().__init__('{} was not registered in the service provider.'.format(service))


class ServicesManager(object):
    T = TypeVar('T')

    def __init__(self):
        self.services: Dict[type, ServiceWrapper] = {}

    def bind_from_instance(self, interface: T, instance: Type[T]):
        self.services[interface] = ServiceWrapper(interface, instance)

    def bind_self_from_instance(self, instance: object):
        instance_type = type(instance)
        self.services[instance_type] = ServiceWrapper(instance_type, instance)

    def bind(self, interface: T, service_type: Type[T]) -> NoReturn:
        self.services[interface] = ServiceWrapper(service_type)

    def bind_self(self, service_type: type):
        self.services[service_type] = ServiceWrapper(service_type)

    def resolve(self, interface: T) -> T:
        services = self.services
        if interface not in services:
            raise ServiceWasNotRegistered(interface)

        return services[interface].instance

    def initialize(self) -> NoReturn:
        self._init_dependencies()
        self._resolve_graph()

    def _init_dependencies(self) -> NoReturn:
        for interface, service in self.services.items():
            for key, value in get_type_hints(interface.__init__).items():
                if key != 'self' and key != 'args' and key != 'kwargs':
                    service.dependencies.append(self.services[value])

    def _resolve_graph(self) -> NoReturn:
        for srv_type, srv in self.services.items():
            if not srv.instance:
                self._instanciate_object(srv)

    def _instanciate_object(self, service: ServiceWrapper) -> NoReturn:
        service.instance = Dummy()
        dependencies: List[ServiceWrapper] = service.dependencies
        if not dependencies:
            service.instance = service.service_type
        elif type(service) is not service.service_type:
            for dep in dependencies:
                if type(dep.instance) is Dummy:
                    raise CircularReferenceError(
                        'Circular dependency between {} and {}'.format(service.service_type, dep))
                self._instanciate_object(dep)
        service.instance = service.service_type(*[dep.instance for dep in service.dependencies])

