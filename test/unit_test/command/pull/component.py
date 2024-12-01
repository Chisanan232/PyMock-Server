import re
from collections import namedtuple
from pathlib import Path
from typing import Union
from unittest.mock import patch

import pytest

from pymock_api.command.pull.component import SubCmdPullComponent

ExpectResult = namedtuple(
    "ExpectResult", ("should_run_client_request", "should_run_json_read", "should_run_deserialize_api_doc_config")
)


class TestSubCmdPullComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdPullComponent:
        return SubCmdPullComponent()

    @pytest.mark.parametrize(
        ("url", "config_file", "expect_result"),
        [
            ("https://example.com", "", ExpectResult(True, False, True)),
            ("", "example.json", ExpectResult(False, True, True)),
            ("", Path("example.json"), ExpectResult(False, True, True)),
            ("https://example.com", "example.json", ExpectResult(True, False, True)),
        ],
    )
    def test__get_openapi_doc_config(
        self,
        component: SubCmdPullComponent,
        url: str,
        config_file: Union[str, Path],
        expect_result: ExpectResult,
    ):
        # Mock
        with patch("pymock_api.command.pull.component.URLLibHTTPClient.request") as mock_client_request:
            with patch("pymock_api.command.pull.component.JSON.read") as mock_json_read:
                with patch(
                    "pymock_api.command.pull.component.deserialize_api_doc_config"
                ) as mock_deserialize_api_doc_config:
                    # Run target function
                    component._get_openapi_doc_config(url=url, config_file=config_file)

                    # Verify
                    if expect_result.should_run_client_request:
                        mock_client_request.assert_called_once_with(method="GET", url=url)
                    else:
                        mock_client_request.assert_not_called()

                    if expect_result.should_run_json_read:
                        mock_json_read.assert_called_once_with(path=str(config_file))
                    else:
                        mock_json_read.assert_not_called()

                    if expect_result.should_run_deserialize_api_doc_config:
                        mock_deserialize_api_doc_config.assert_called_once()
                    else:
                        mock_deserialize_api_doc_config.assert_not_called()

    @pytest.mark.parametrize(
        ("url", "config_file"),
        [
            (None, ""),
            ("", None),
            ("", ""),
            (None, None),
        ],
    )
    def test__get_openapi_doc_config_with_invalid_args(
        self,
        component: SubCmdPullComponent,
        url: str,
        config_file: Union[str, Path],
    ):
        # Mock
        with patch("pymock_api.command.pull.component.URLLibHTTPClient.request") as mock_client_request:
            with patch("pymock_api.command.pull.component.JSON.read") as mock_json_read:
                with patch(
                    "pymock_api.command.pull.component.deserialize_api_doc_config"
                ) as mock_deserialize_api_doc_config:
                    # Run target function
                    with pytest.raises(ValueError) as exc_info:
                        component._get_openapi_doc_config(url=url, config_file=config_file)

                    # Verify
                    assert re.search(r".{0,64}URL.{0,64}configuration file.{0,64}", str(exc_info.value), re.IGNORECASE)

                    mock_client_request.assert_not_called()
                    mock_json_read.assert_not_called()
                    mock_deserialize_api_doc_config.assert_not_called()
