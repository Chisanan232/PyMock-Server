from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Union


class BaseTestCaseFactory(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_test_case(cls) -> Union[List, Tuple]:
        pass

    @classmethod
    @abstractmethod
    def load(cls, *args, **kwargs) -> None:
        pass
