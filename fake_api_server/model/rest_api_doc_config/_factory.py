from abc import ABCMeta, abstractmethod

from ._base_model_adapter import (
    BaseAPIAdapter,
    BaseFormatModelAdapter,
    BaseRefPropertyDetailAdapter,
    BaseRequestParameterAdapter,
    BaseResponsePropertyAdapter,
)


class _BaseAdapterFactory(metaclass=ABCMeta):
    @abstractmethod
    def generate_value_format(self, **kwargs) -> BaseFormatModelAdapter:
        pass

    @abstractmethod
    def generate_property_details(self, **kwargs) -> BaseRefPropertyDetailAdapter:
        pass

    @abstractmethod
    def generate_request_params(self, **kwargs) -> BaseRequestParameterAdapter:
        pass

    @abstractmethod
    def generate_response_props(self, **kwargs) -> BaseResponsePropertyAdapter:
        pass

    @abstractmethod
    def generate_api(self, **kwargs) -> BaseAPIAdapter:
        pass
