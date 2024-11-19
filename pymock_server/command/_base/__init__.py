from abc import ABCMeta, abstractmethod


class BaseAutoLoad(metaclass=ABCMeta):
    py_module: str = ""

    @staticmethod
    @abstractmethod
    def import_all() -> None:
        pass
