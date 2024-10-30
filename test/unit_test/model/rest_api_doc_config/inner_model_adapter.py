from typing import Type, Union

import pytest

from pymock_server.model.api_config.apis import ResponseStrategy
from pymock_server.model.rest_api_doc_config._model_adapter import PropertyDetailAdapter


class TestPropertyDetailAdapter:

    @pytest.mark.parametrize(
        ("strategy", "expected_type"),
        [
            (ResponseStrategy.OBJECT, PropertyDetailAdapter),
        ],
    )
    def test_generate_empty_response(self, strategy: ResponseStrategy, expected_type: Union[type, Type]):
        empty_resp = PropertyDetailAdapter.generate_empty_response()
        assert isinstance(empty_resp, expected_type)
