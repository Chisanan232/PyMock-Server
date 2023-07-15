import json
import pathlib
import re
import sys
from typing import Any, Callable, Optional

from ..._utils.api_client import URLLibHTTPClient
from ...model import (
    SubcmdCheckArguments,
    SwaggerConfig,
    deserialize_swagger_api_config,
    load_config,
)
from ...model.api_config import APIConfig
from ...model.api_config import APIParameter as MockedAPIParameter
from ...model.swagger_config import API as SwaggerAPI
from ...model.swagger_config import APIParameter as SwaggerAPIParameter


class SubCmdCheckComponent:
    def __init__(self):
        super().__init__()
        self._validity_comp = ValidityChecking()
        self._swagger_diff_comp = SwaggerDiffChecking()

    def process(self, args: SubcmdCheckArguments) -> None:
        api_config: Optional[APIConfig] = load_config(path=args.config_path)

        valid_api_config = self._validity_comp.run(args=args, api_config=api_config)
        if args.swagger_doc_url:
            self._swagger_diff_comp.run(args, valid_api_config)


class ValidityChecking:
    def __init__(self):
        super().__init__()
        self._stop_if_fail: Optional[bool] = None
        self._config_is_wrong: bool = False

    def run(self, args: SubcmdCheckArguments, api_config: Optional[APIConfig]) -> APIConfig:
        self._stop_if_fail = args.stop_if_fail
        api_config = self.check(api_config)
        if self._config_is_wrong:
            print("Configuration is invalid.")
            if self._stop_if_fail or not args.swagger_doc_url:
                sys.exit(1)
        else:
            print("Configuration is valid.")
            if not args.swagger_doc_url:
                sys.exit(0)
        return api_config

    def check(self, api_config: Optional[APIConfig]) -> APIConfig:
        # # Check whether it has anything in configuration or not
        if not self._setting_should_not_be_none(
            config_key="",
            config_value=api_config,
            err_msg="Configuration is empty.",
        ):
            self._exit_program(
                msg="⚠️  Configuration is invalid.",
                exit_code=1,
            )
        # # Check the section *mocked_apis* (first layer) of configuration
        # NOTE: It's the normal behavior of code implementation. It must have something of property *MockAPIs.apis*
        # if it has anything within key *mocked_apis*.
        assert api_config is not None  # Here is strange
        if not self._setting_should_not_be_none(
            config_key="mocked_apis",
            config_value=api_config.apis,
        ):
            self._exit_program(
                msg="⚠️  Configuration is invalid.",
                exit_code=1,
            )
        assert api_config.apis
        self._setting_should_not_be_none(
            config_key="mocked_apis.<API name>",
            config_value=api_config.apis.apis,
        )
        # # Check each API content at first layer is *mocked_apis* of configuration
        for one_api_name, one_api_config in api_config.apis.apis.items():
            # # Check the section *mocked_apis.<API name>* (second layer) of configuration
            if not self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}",
                config_value=one_api_config,
            ):
                continue

            # # Check the section *mocked_apis.<API name>.<property>* (third layer) of configuration (not
            # # include the layer about API name, should be the first layer under API name)
            assert one_api_config
            self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.url",
                config_value=one_api_config.url,
            )
            if not self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http",
                config_value=one_api_config.http,
            ):
                continue

            # # Check the section *mocked_apis.<API name>.http.<property>* (forth layer) of configuration
            assert one_api_config.http
            if not self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.request",
                config_value=one_api_config.http.request,
            ):
                continue

            assert one_api_config.http.request
            if not self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.request.method",
                config_value=one_api_config.http.request.method,
            ):
                continue
            assert one_api_config.http.request.method
            self._setting_should_be_valid(
                config_key=f"mocked_apis.{one_api_name}.http.request.method",
                config_value=one_api_config.http.request.method.upper(),
                criteria=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTION"],
            )

            if not self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.response",
                config_value=one_api_config.http.response,
            ):
                continue

            assert one_api_config.http.response
            self._setting_should_not_be_none(
                config_key=f"mocked_apis.{one_api_name}.http.response.value",
                config_value=one_api_config.http.response.value,
                valid_callback=self._chk_response_value_validity,
            )
        return api_config

    def _chk_response_value_validity(self, config_key: str, config_value: Any) -> bool:
        try:
            json.loads(config_value)
        except:
            if re.search(r"\w{1,32}\.\w{1,8}", config_value):
                if not pathlib.Path(config_value).exists():
                    print("The file which is the response content doesn't exist.")
                    self._config_is_wrong = True
                    if self._stop_if_fail:
                        sys.exit(1)
                    return False
            # else:
            #     print("Data content format is incorrect")
            #     sys.exit(1)
            return True
        else:
            return True

    def _setting_should_not_be_none(
        self,
        config_key: str,
        config_value: Any,
        valid_callback: Optional[Callable] = None,
        err_msg: Optional[str] = None,
    ) -> bool:
        if config_value is None:
            print(err_msg if err_msg else f"Configuration *{config_key}* content cannot be empty.")
            self._config_is_wrong = True
            if self._stop_if_fail:
                sys.exit(1)
            return False
        else:
            if valid_callback:
                return valid_callback(config_key, config_value)
            return True

    def _setting_should_be_valid(
        self, config_key: str, config_value: Any, criteria: list, valid_callback: Optional[Callable] = None
    ) -> None:
        if not isinstance(criteria, list):
            raise TypeError("The argument *criteria* only accept 'list' type value.")

        if config_value not in criteria:
            is_valid = False
        else:
            is_valid = True

        if not is_valid:
            print(f"Configuration *{config_key}* value is invalid.")
            self._config_is_wrong = True
            if self._stop_if_fail:
                sys.exit(1)
        else:
            if valid_callback:
                valid_callback(config_key, config_value, criteria)

    def _exit_program(self, msg: str, exit_code: int = 0) -> None:
        print(msg)
        sys.exit(exit_code)


class SwaggerDiffChecking:
    def __init__(self):
        super().__init__()
        self._api_client = URLLibHTTPClient()
        self._stop_if_fail: Optional[bool] = None
        self._config_is_wrong: bool = False

    def run(self, args: SubcmdCheckArguments, api_config: APIConfig) -> None:
        self._stop_if_fail = args.stop_if_fail
        self.check(args, api_config)
        if self._config_is_wrong:
            self._exit_program(
                msg=f"⚠️  The configuration has something wrong or miss with Swagger API document {args.swagger_doc_url}.",
                exit_code=1,
            )
        else:
            self._exit_program(
                msg=f"🍻  All mock APIs are already be updated with Swagger API document {args.swagger_doc_url}.",
                exit_code=0,
            )

    def check(self, args: SubcmdCheckArguments, current_api_config: APIConfig) -> None:
        assert current_api_config
        mocked_apis_config = current_api_config.apis
        base_info = mocked_apis_config.base  # type: ignore[union-attr]
        mocked_apis_info = mocked_apis_config.apis  # type: ignore[union-attr]
        if base_info:
            mocked_apis_path = list(map(lambda p: f"{base_info.url}{p.url}", mocked_apis_info.values()))
        else:
            mocked_apis_path = list(map(lambda p: p.url, mocked_apis_info.values()))
        swagger_api_doc_model = self._get_swagger_config(swagger_url=args.swagger_doc_url)
        for swagger_api_config in swagger_api_doc_model.paths:
            # Check API path
            if args.check_api_path and swagger_api_config.path not in mocked_apis_path:
                self._chk_fail_error_log(
                    f"⚠️  Miss API. Path: {swagger_api_config.path}",
                    stop_if_fail=args.stop_if_fail,
                )
                continue

            mocked_api_config = mocked_apis_config.get_api_config_by_url(  # type: ignore[union-attr]
                swagger_api_config.path, base=base_info
            )
            api_http_config = mocked_api_config.http  # type: ignore[union-attr]

            if (
                args.check_api_http_method
                and str(swagger_api_config.http_method).upper() != api_http_config.request.method.upper()  # type: ignore[union-attr]
            ):
                self._chk_fail_error_log(
                    f"⚠️  Miss the API {swagger_api_config.path} with HTTP method {swagger_api_config.http_method}.",
                    stop_if_fail=args.stop_if_fail,
                )

            # Check API parameters
            if args.check_api_parameters:
                # FIXME: target configuration may have redunden settings.
                for swagger_one_api_param in swagger_api_config.parameters:
                    api_param_config = api_http_config.request.get_one_param_by_name(  # type: ignore[union-attr]
                        swagger_one_api_param.name
                    )
                    if api_param_config is None:
                        self._chk_fail_error_log(
                            f"⚠️  Miss the API parameter {swagger_one_api_param.name}.",
                            stop_if_fail=args.stop_if_fail,
                        )
                        continue
                    if swagger_one_api_param.required is not api_param_config.required:
                        self._chk_api_params_error_log(
                            api_config=api_param_config,
                            param="required",
                            swagger_api_config=swagger_api_config,
                            swagger_api_param=swagger_one_api_param,
                            stop_if_fail=args.stop_if_fail,
                        )
                    if swagger_one_api_param.value_type != api_param_config.value_type:
                        self._chk_api_params_error_log(
                            api_config=api_param_config,
                            param="value_type",
                            swagger_api_config=swagger_api_config,
                            swagger_api_param=swagger_one_api_param,
                            stop_if_fail=args.stop_if_fail,
                        )
                    if swagger_one_api_param.default != api_param_config.default:
                        self._chk_api_params_error_log(
                            api_config=api_param_config,
                            param="default",
                            swagger_api_config=swagger_api_config,
                            swagger_api_param=swagger_one_api_param,
                            stop_if_fail=args.stop_if_fail,
                        )

            # TODO: Implement the checking detail of HTTP response
            # Check API response
            api_resp = swagger_api_config.response

    def _get_swagger_config(self, swagger_url: str) -> SwaggerConfig:
        swagger_api_doc: dict = self._api_client.request(method="GET", url=swagger_url)
        return deserialize_swagger_api_config(data=swagger_api_doc)

    def _chk_api_params_error_log(
        self,
        api_config: MockedAPIParameter,
        param: str,
        swagger_api_config: SwaggerAPI,
        swagger_api_param: SwaggerAPIParameter,
        stop_if_fail: bool,
    ) -> None:
        which_property_error = (
            f"⚠️  Incorrect API parameter property *{param}* of "
            f"API '{swagger_api_config.http_method} {swagger_api_config.path}'."
        )
        swagger_api_config_value = f"\n  * Swagger API document: {getattr(swagger_api_param, param)}"
        config_value = f"\n  * Current config: {getattr(api_config, param)}"
        self._chk_fail_error_log(
            log=which_property_error + swagger_api_config_value + config_value, stop_if_fail=stop_if_fail
        )

    def _chk_fail_error_log(self, log: str, stop_if_fail: bool) -> None:
        print(log)
        self._config_is_wrong = True
        if stop_if_fail:
            sys.exit(1)

    def _exit_program(self, msg: str, exit_code: int = 0) -> None:
        print(msg)
        sys.exit(exit_code)
