from abc import ABCMeta, abstractmethod

from urllib3 import PoolManager


class BaseAPIClient(metaclass=ABCMeta):
    @abstractmethod
    def request(self, *args, **kwargs):
        pass


class URLLibHTTPClient(BaseAPIClient):
    def __init__(self):
        self._manager = PoolManager()

    def request(self, method: str, url: str) -> dict:
        return self._manager.request(method=method, url=url).json()
