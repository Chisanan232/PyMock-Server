from abc import ABCMeta, abstractmethod


class BaseAutoLoad(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def import_all() -> None:
        pass
