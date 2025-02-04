import json
import logging
from argparse import Namespace
from typing import Callable, List, Optional, Type
from unittest.mock import MagicMock, Mock, patch

import pytest
from yaml import load as yaml_load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader  # type: ignore

from test._values import (
    SubCommand,
    _API_Doc_Source,
    _API_Doc_Source_File,
    _Base_URL,
    _Default_Base_File_Path,
    _Default_Include_Template_Config,
    _Test_Config,
    _Test_Divide_Api,
    _Test_Divide_Http,
    _Test_Divide_Http_Request,
    _Test_Divide_Http_Response,
    _Test_Dry_Run,
    _Test_Request_With_Https,
)
from test.unit_test.command._base.process import BaseCommandProcessorTestSpec

from fake_api_server._utils import YAML
from fake_api_server.command.rest_server.pull.process import SubCmdPull
from fake_api_server.command.subcommand import SubCommandLine
from fake_api_server.model import SubcmdPullArguments, deserialize_api_doc_config
from fake_api_server.model.rest_api_doc_config.base_config import (
    set_component_definition,
)
from fake_api_server.model.subcmd_common import SysArg

from ._test_case import SubCmdPullTestCaseFactory

logger = logging.getLogger(__name__)


SubCmdPullTestCaseFactory.load()
SUBCMD_PULL_TEST_CASE = SubCmdPullTestCaseFactory.get_test_case()


class FakeYAML(YAML):
    pass


class TestSubCmdPull(BaseCommandProcessorTestSpec):
    @pytest.fixture(scope="function")
    def cmd_ps(self) -> SubCmdPull:
        return SubCmdPull()

    @pytest.mark.parametrize(
        ("swagger_config", "dry_run", "expected_config"),
        SUBCMD_PULL_TEST_CASE,
    )
    def test_with_command_processor(
        self, swagger_config: str, dry_run: bool, expected_config: str, object_under_test: Callable
    ):
        kwargs = {
            "swagger_config": swagger_config,
            "dry_run": dry_run,
            "expected_config": expected_config,
            "cmd_ps": object_under_test,
        }
        self._test_process(**kwargs)

    @pytest.mark.parametrize(
        ("swagger_config", "dry_run", "expected_config"),
        SUBCMD_PULL_TEST_CASE,
    )
    def test_with_run_entry_point(
        self, swagger_config: str, dry_run: bool, expected_config: str, entry_point_under_test: Callable
    ):
        kwargs = {
            "swagger_config": swagger_config,
            "dry_run": dry_run,
            "expected_config": expected_config,
            "cmd_ps": entry_point_under_test,
        }
        self._test_process(**kwargs)

    def _test_process(self, swagger_config: str, dry_run: bool, expected_config: str, cmd_ps: Callable):
        FakeYAML.write = MagicMock()
        base_url = _Base_URL if ("has-base" in swagger_config and "has-base" in expected_config) else ""
        mock_parser_arg = SubcmdPullArguments(
            subparser_structure=SysArg.parse([SubCommand.RestServer, SubCommand.Pull]),
            request_with_https=_Test_Request_With_Https,
            source=_API_Doc_Source,
            source_file=_API_Doc_Source_File,
            config_path=_Test_Config,
            base_url=base_url,
            base_file_path=_Default_Base_File_Path,
            include_template_config=_Default_Include_Template_Config,
            dry_run=dry_run,
            divide_api=_Test_Divide_Api,
            divide_http=_Test_Divide_Http,
            divide_http_request=_Test_Divide_Http_Request,
            divide_http_response=_Test_Divide_Http_Response,
        )
        cmd_parser = Mock()

        with open(swagger_config, "r") as file:
            swagger_json_data = json.loads(file.read())

        with open(expected_config, "r") as file:
            expected_config_data = yaml_load(file, Loader=Loader)

        set_component_definition(swagger_json_data.get("definitions", {}))
        with patch("sys.argv", self._given_command_line()):
            with patch(
                "fake_api_server.command._common.component.YAML", return_value=FakeYAML
            ) as mock_instantiate_writer:
                with patch(
                    "fake_api_server.command.rest_server.pull.component.URLLibHTTPClient.request",
                    return_value=swagger_json_data,
                ) as mock_swagger_request:
                    # Run target function
                    logger.debug(f"run target function: {cmd_ps}")
                    cmd_ps(cmd_parser, mock_parser_arg)

                    mock_instantiate_writer.assert_called_once()
                    mock_swagger_request.assert_called_once_with(method="GET", url=f"http://{_API_Doc_Source}")

                    # Run one core logic of target function
                    under_test_api_config = deserialize_api_doc_config(swagger_json_data).to_api_config(
                        mock_parser_arg.base_url
                    )
                    under_test_api_config.set_template_in_config = False
                    under_test_config_data = under_test_api_config.serialize()
                    assert expected_config_data["name"] == under_test_config_data["name"]
                    assert expected_config_data["description"] == under_test_config_data["description"]
                    assert len(expected_config_data["mocked_apis"].keys()) == len(
                        under_test_config_data["mocked_apis"].keys()
                    )
                    assert len(expected_config_data["mocked_apis"]["apis"].keys()) == len(
                        under_test_config_data["mocked_apis"]["apis"].keys()
                    )
                    expected_config_data_keys = sorted(expected_config_data["mocked_apis"]["apis"].keys())
                    under_test_config_data_keys = sorted(under_test_config_data["mocked_apis"]["apis"].keys())
                    for expected_key, under_test_key in zip(expected_config_data_keys, under_test_config_data_keys):
                        assert expected_key == under_test_key
                        expected_api_config = expected_config_data["mocked_apis"]["apis"][expected_key]
                        under_test_api_config = under_test_config_data["mocked_apis"]["apis"][under_test_key]
                        if expected_key != "base":
                            # Verify mock API URL
                            assert expected_api_config["url"] == under_test_api_config["url"]
                            # Verify mock API request properties - HTTP method
                            assert expected_api_config["http"]["request"] is not None
                            assert under_test_api_config["http"]["request"] is not None
                            assert (
                                expected_api_config["http"]["request"]["method"]
                                == under_test_api_config["http"]["request"]["method"]
                            )
                            # Verify mock API request properties - request parameters
                            assert (
                                expected_api_config["http"]["request"]["parameters"]
                                == under_test_api_config["http"]["request"]["parameters"]
                            )
                            # Verify mock API response properties
                            assert (
                                expected_api_config["http"]["response"]["strategy"]
                                == under_test_api_config["http"]["response"]["strategy"]
                            )
                            assert expected_api_config["http"]["response"].get("value", None) == under_test_api_config[
                                "http"
                            ]["response"].get("value", None)
                            assert expected_api_config["http"]["response"].get("path", None) == under_test_api_config[
                                "http"
                            ]["response"].get("path", None)
                            assert expected_api_config["http"]["response"].get(
                                "properties", None
                            ) == under_test_api_config["http"]["response"].get("properties", None)
                        else:
                            # Verify base info
                            assert expected_api_config == under_test_api_config

                    if mock_parser_arg.dry_run:
                        if len(str(expected_config_data)) > 1000:
                            FakeYAML.write.assert_called_once_with(
                                path="dry-run_result.yaml", config=expected_config_data, mode="w+"
                            )
                        else:
                            FakeYAML.write.assert_not_called()
                    else:
                        FakeYAML.write.assert_called_once_with(
                            path=_Test_Config, config=expected_config_data, mode="w+"
                        )

    def _given_command_line(self) -> List[str]:
        return ["rest-server", "pull"]

    def _given_cmd_args_namespace(self) -> Namespace:
        args_namespace = Namespace()
        args_namespace.subcommand = SubCommand.RestServer
        setattr(args_namespace, SubCommand.RestServer, SubCommand.Pull)
        args_namespace.request_with_https = _Test_Request_With_Https
        args_namespace.source = _API_Doc_Source
        args_namespace.source_file = _API_Doc_Source_File
        args_namespace.base_url = _Base_URL
        args_namespace.base_file_path = _Default_Base_File_Path
        args_namespace.config_path = _Test_Config
        args_namespace.include_template_config = _Default_Include_Template_Config
        args_namespace.dry_run = _Test_Dry_Run
        args_namespace.divide_api = _Test_Divide_Api
        args_namespace.divide_http = _Test_Divide_Http
        args_namespace.divide_http_request = _Test_Divide_Http_Request
        args_namespace.divide_http_response = _Test_Divide_Http_Response
        return args_namespace

    def _given_subcmd(self) -> Optional[SysArg]:
        return SysArg(
            pre_subcmd=SysArg(pre_subcmd=SysArg(subcmd=SubCommandLine.Base), subcmd=SubCommandLine.RestServer),
            subcmd=SubCommandLine.Pull,
        )

    def _expected_argument_type(self) -> Type[SubcmdPullArguments]:
        return SubcmdPullArguments
