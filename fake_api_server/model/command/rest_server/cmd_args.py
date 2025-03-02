import json
from abc import ABC, ABCMeta, abstractmethod
from argparse import Namespace
from dataclasses import dataclass
from typing import List, Optional, Union

from fake_api_server._utils.file import Format
from fake_api_server.model.api_config.apis import ResponseStrategy
from fake_api_server.model.command.rest_server._sample import SampleType
from fake_api_server.model.subcmd_common import SysArg


@dataclass(frozen=True)
class ParserArguments(metaclass=ABCMeta):
    """*The data object for the arguments from parsing the command line of PyFake-API-Server program*"""

    subparser_structure: SysArg

    @staticmethod
    def parse_subparser_cmd(args: Namespace) -> SysArg:
        major_subcmd = args.subcommand
        major_subcmd_feature = args.__dict__[major_subcmd]
        return SysArg.parse([major_subcmd, major_subcmd_feature])

    @classmethod
    @abstractmethod
    def deserialize(cls, args: Namespace) -> "ParserArguments":
        pass


@dataclass(frozen=True)
class _BaseSubCmdArgumentsSavingConfig(ParserArguments, ABC):
    config_path: str
    include_template_config: bool
    base_file_path: str
    base_url: str
    dry_run: bool
    divide_api: bool
    divide_http: bool
    divide_http_request: bool
    divide_http_response: bool


@dataclass(frozen=True)
class SubcmdRunArguments(ParserArguments):
    config: str
    app_type: str
    bind: str
    workers: int
    log_level: str
    daemon: bool
    access_log_file: str

    @classmethod
    def deserialize(cls, args: Namespace) -> "SubcmdRunArguments":
        return SubcmdRunArguments(
            subparser_structure=ParserArguments.parse_subparser_cmd(args),
            config=args.config,
            app_type=args.app_type,
            bind=args.bind,
            workers=args.workers,
            log_level=args.log_level,
            daemon=args.daemon,
            access_log_file=args.access_log_file,
        )


@dataclass(frozen=True)
class SubcmdAddArguments(_BaseSubCmdArgumentsSavingConfig):
    tag: str
    api_path: str
    http_method: str
    parameters: List[dict]
    response_strategy: ResponseStrategy
    response_value: List[Union[str, dict]]

    @classmethod
    def deserialize(cls, args: Namespace) -> "SubcmdAddArguments":
        args.response_strategy = ResponseStrategy(args.response_strategy)
        if args.parameters:
            args.parameters = list(map(lambda p: json.loads(p), args.parameters))
        if args.response_value:
            args.response_value = list(
                map(
                    lambda resp: json.loads(resp) if args.response_strategy is ResponseStrategy.OBJECT else resp,
                    args.response_value,
                )
            )
        return SubcmdAddArguments(
            subparser_structure=ParserArguments.parse_subparser_cmd(args),
            config_path=args.config_path,
            tag=args.tag,
            api_path=args.api_path,
            http_method=args.http_method,
            parameters=args.parameters,
            response_strategy=args.response_strategy,
            response_value=args.response_value,
            # Common arguments about saving configuration
            include_template_config=args.include_template_config,
            base_file_path=args.base_file_path,
            base_url=args.base_url,
            divide_api=args.divide_api,
            divide_http=args.divide_http,
            divide_http_request=args.divide_http_request,
            divide_http_response=args.divide_http_response,
            dry_run=args.dry_run,
        )

    def api_info_is_complete(self) -> bool:
        def _string_is_not_empty(s: Optional[str]) -> bool:
            if s is not None:
                s = s.replace(" ", "")
                return s != ""
            return False

        string_chksum = list(map(_string_is_not_empty, [self.config_path, self.api_path]))
        return False not in string_chksum


@dataclass(frozen=True)
class SubcmdCheckArguments(ParserArguments):
    config_path: str
    swagger_doc_url: str
    stop_if_fail: bool
    check_api_path: bool
    check_api_http_method: bool
    check_api_parameters: bool

    @classmethod
    def deserialize(cls, args: Namespace) -> "SubcmdCheckArguments":
        if hasattr(args, "check_entire_api") and args.check_entire_api:
            args.check_api_path = True
            args.check_api_http_method = True
            args.check_api_parameters = True
        return SubcmdCheckArguments(
            subparser_structure=ParserArguments.parse_subparser_cmd(args),
            config_path=args.config_path,
            swagger_doc_url=args.swagger_doc_url,
            stop_if_fail=args.stop_if_fail,
            check_api_path=args.check_api_path,
            check_api_http_method=args.check_api_http_method,
            check_api_parameters=args.check_api_parameters,
        )


@dataclass(frozen=True)
class SubcmdGetArguments(ParserArguments):
    config_path: str
    show_detail: bool
    show_as_format: Format
    api_path: str
    http_method: str

    @classmethod
    def deserialize(cls, args: Namespace) -> "SubcmdGetArguments":
        return SubcmdGetArguments(
            subparser_structure=ParserArguments.parse_subparser_cmd(args),
            config_path=args.config_path,
            show_detail=args.show_detail,
            show_as_format=Format[str(args.show_as_format).upper()],
            api_path=args.api_path,
            http_method=args.http_method,
        )


@dataclass(frozen=True)
class SubcmdSampleArguments(ParserArguments):
    generate_sample: bool
    print_sample: bool
    sample_output_path: str
    sample_config_type: SampleType

    @classmethod
    def deserialize(cls, args: Namespace) -> "SubcmdSampleArguments":
        return SubcmdSampleArguments(
            subparser_structure=ParserArguments.parse_subparser_cmd(args),
            generate_sample=args.generate_sample,
            print_sample=args.print_sample,
            sample_output_path=args.file_path,
            sample_config_type=SampleType[str(args.sample_config_type).upper()],
        )


@dataclass(frozen=True)
class SubcmdPullArguments(_BaseSubCmdArgumentsSavingConfig):
    request_with_https: bool
    source: str
    source_file: str

    @classmethod
    def deserialize(cls, args: Namespace) -> "SubcmdPullArguments":
        return SubcmdPullArguments(
            subparser_structure=ParserArguments.parse_subparser_cmd(args),
            request_with_https=args.request_with_https,
            source=args.source,
            source_file=args.source_file,
            config_path=args.config_path,
            # Common arguments about saving configuration
            include_template_config=args.include_template_config,
            base_file_path=args.base_file_path,
            base_url=args.base_url,
            divide_api=args.divide_api,
            divide_http=args.divide_http,
            divide_http_request=args.divide_http_request,
            divide_http_response=args.divide_http_response,
            dry_run=args.dry_run,
        )
