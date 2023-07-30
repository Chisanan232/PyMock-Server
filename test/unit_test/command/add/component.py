import re
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest

from pymock_api import APIConfig
from pymock_api._utils.file_opt import YAML
from pymock_api.command.add.component import SubCmdAddComponent
from pymock_api.model import MockAPI, generate_empty_config
from pymock_api.model.cmd_args import SubcmdAddArguments

from ...._values import (
    _Test_Config,
    _Test_HTTP_Method,
    _Test_HTTP_Resp,
    _Test_SubCommand_Add,
    _Test_URL,
    _TestConfig,
)


class FakeYAML(YAML):
    pass


class TestSubCmdConfigComponent:
    @pytest.fixture(scope="class")
    def component(self) -> SubCmdAddComponent:
        return SubCmdAddComponent()

    def test_assert_error_with_empty_args(self, component: SubCmdAddComponent):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        invalid_args = SubcmdAddArguments(
            subparser_name=_Test_SubCommand_Add,
            print_sample=False,
            generate_sample=True,
            sample_output_path="",
            api_config_path="",
            api_path="",
            http_method="",
            parameters=[],
            response="",
        )

        # Run target function to test
        with patch("pymock_api.command.add.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with pytest.raises(AssertionError) as exc_info:
                component.process(invalid_args)

            # Verify result
            assert re.search(r"Option '.{1,20}' value cannot be empty.", str(exc_info.value), re.IGNORECASE)
            mock_instantiate_writer.assert_called_once()
            FakeYAML.serialize.assert_called_once()
            FakeYAML.write.assert_not_called()

    @pytest.mark.parametrize(
        ("file_exist", "load_config_result"),
        [
            (False, None),
            (True, generate_empty_config()),
            (True, None),
        ],
    )
    def test_get_api_config(
        self, file_exist: bool, load_config_result: Optional[APIConfig], component: SubCmdAddComponent
    ):
        with patch("pymock_api.command.add.component.load_config", return_value=load_config_result) as mock_load_config:
            with patch("pymock_api.command.add.component.generate_empty_config") as mock_generate_empty_config:
                with patch("os.path.exists", return_value=file_exist) as mock_path_exist:
                    args = SubcmdAddArguments(
                        subparser_name=_Test_SubCommand_Add,
                        print_sample=False,
                        generate_sample=False,
                        sample_output_path="",
                        api_config_path=_Test_Config,
                        api_path=_Test_URL,
                        http_method="GET",
                        parameters=[],
                        response="OK",
                    )
                    component._get_api_config(args)

                    mock_path_exist.assert_called_once_with(_Test_Config)
                    if file_exist:
                        mock_load_config.assert_called_once_with(_Test_Config)
                        if load_config_result:
                            mock_generate_empty_config.assert_not_called()
                        else:
                            mock_generate_empty_config.assert_called_once()
                    else:
                        mock_load_config.assert_not_called()
                        mock_generate_empty_config.assert_called_once()

    @pytest.mark.parametrize(
        ("http_method", "parameters", "response"),
        [
            (None, [], None),
            (
                "POST",
                [{"name": "arg1", "required": False, "default": "val1", "type": "str"}],
                "This is PyTest response",
            ),
        ],
    )
    def test_add_valid_api(
        self, http_method: Optional[str], parameters: List[dict], response: Optional[str], component: SubCmdAddComponent
    ):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        with patch("pymock_api.command.add.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with patch("os.path.exists", return_value=False) as mock_path_exist:
                args = SubcmdAddArguments(
                    subparser_name=_Test_SubCommand_Add,
                    print_sample=False,
                    generate_sample=False,
                    sample_output_path="",
                    api_config_path=_Test_Config,
                    api_path=_Test_URL,
                    http_method=http_method,
                    parameters=parameters,
                    response=response,
                )
                component.process(args)

                api_config = generate_empty_config()
                api_config = component._generate_api_config(api_config, args)

                mock_path_exist.assert_called_once_with(_Test_Config)
                mock_instantiate_writer.assert_called_once()
                FakeYAML.write.assert_called_once_with(path=_Test_Config, config=api_config.serialize())

    @pytest.mark.parametrize(
        ("http_method", "parameters", "response"),
        [
            (
                "POST",
                [{"name": "arg1", "required": False, "default": "val1", "type": "str", "invalid_key": "val"}],
                "This is PyTest response",
            ),
        ],
    )
    def test_add_invalid_api(
        self, http_method: Optional[str], parameters: List[dict], response: Optional[str], component: SubCmdAddComponent
    ):
        # Mock functions
        FakeYAML.serialize = MagicMock()
        FakeYAML.write = MagicMock()

        with patch("pymock_api.command.add.component.YAML", return_value=FakeYAML) as mock_instantiate_writer:
            with patch("os.path.exists", return_value=False) as mock_path_exist:
                args = SubcmdAddArguments(
                    subparser_name=_Test_SubCommand_Add,
                    print_sample=False,
                    generate_sample=False,
                    sample_output_path="",
                    api_config_path=_Test_Config,
                    api_path=_Test_URL,
                    http_method=http_method,
                    parameters=parameters,
                    response=response,
                )
                with pytest.raises(SystemExit) as exc_info:
                    component.process(args)
                assert str(exc_info.value) == "1"

                mock_path_exist.assert_called_once_with(_Test_Config)
                mock_instantiate_writer.assert_called_once()
                FakeYAML.write.assert_not_called()
