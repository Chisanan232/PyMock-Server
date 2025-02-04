import importlib
import inspect
import logging
import os
import sys
from abc import ABCMeta, abstractmethod
from argparse import ArgumentParser
from typing import Dict, Optional, cast

from fake_api_server._utils.file import Format
from fake_api_server.command._base.component import BaseSubCmdComponent
from fake_api_server.model import MockAPI, load_config
from fake_api_server.model.command.rest_server.cmd_args import SubcmdGetArguments

logger = logging.getLogger(__name__)


class SubCmdGetComponent(BaseSubCmdComponent):
    def process(self, parser: ArgumentParser, args: SubcmdGetArguments) -> None:  # type: ignore[override]
        current_api_config = load_config(path=args.config_path)
        if current_api_config is None:
            logger.error("❌  Empty content in configuration file.")
            sys.exit(1)
        apis_info = current_api_config.apis
        if apis_info.apis is None or (apis_info.apis is not None and len(apis_info.apis.keys())) == 0:  # type: ignore[union-attr]
            logger.error("❌  Cannot find any API setting to mock.")
            sys.exit(1)
        assert apis_info
        specific_api_info = apis_info.get_api_config_by_url(url=args.api_path, base=apis_info.base)
        APIInfoDisplayChain().show(args, specific_api_info)


class _BaseDisplayChain(metaclass=ABCMeta):
    def __init__(self):
        self.displays: Dict[Format, "_BaseDisplayFormat"] = self._get_display_members()
        logger.debug(f"[DEBUG] self.displays: {self.displays}")
        assert self.displays, "The API info display chain cannot be empty."
        self._current_format: Format = Format.TEXT
        self._current_display = self.displays[self._current_format]

    def _get_display_members(self) -> Dict[Format, "_BaseDisplayFormat"]:
        current_module = os.path.basename(__file__).replace(".py", "")
        module_path = ".".join([__package__, current_module])
        members = inspect.getmembers(
            object=importlib.import_module(module_path),
            predicate=lambda c: inspect.isclass(c) and issubclass(c, _BaseDisplayFormat) and not inspect.isabstract(c),
        )

        all_displays = {}
        for m in members:
            cls_obj = m[1]
            cls_inst = cast(_BaseDisplayFormat, cls_obj())
            all_displays[cls_inst.format] = cls_inst

        return all_displays

    @property
    def current_display(self) -> "_BaseDisplayFormat":
        return self._current_display

    def next(self) -> "_BaseDisplayFormat":
        self._current_display = self.displays[self._current_format]
        return self._current_display

    def dispatch(self, format: Format) -> "_BaseDisplayFormat":
        if format not in self.displays.keys():
            logger.error("❌  Invalid valid of option *--show-as-format*.")
            sys.exit(1)

        self._current_format = format
        if self.current_display.is_responsible(format):
            return self.current_display
        else:
            self.next()
            return self.dispatch(format)

    @abstractmethod
    def show(self, args: SubcmdGetArguments, specific_api_info: Optional[MockAPI]) -> None:
        pass


class APIInfoDisplayChain(_BaseDisplayChain):
    def show(self, args: SubcmdGetArguments, api_config: Optional[MockAPI]) -> None:
        if api_config:
            logger.info("🍻  Find the API info which satisfy the conditions.")
            if args.show_detail:
                self.dispatch(format=args.show_as_format).display(api_config)
            sys.exit(0)
        else:
            logger.error("🙅‍♂️  Cannot find the API info with the conditions.")
            sys.exit(1)


class _BaseDisplayFormat(metaclass=ABCMeta):
    @property
    @abstractmethod
    def format(self) -> Format:
        pass

    def is_responsible(self, f: Format) -> bool:
        return self.format == f

    @abstractmethod
    def display(self, api_config: MockAPI) -> None:
        pass


class DisplayAsTextFormat(_BaseDisplayFormat):
    @property
    def format(self) -> Format:
        return Format.TEXT

    def display(self, api_config: MockAPI) -> None:
        logger.info("+--------------- API info ---------------+")
        logger.info(f"+ Path:  {api_config.url}")
        logger.info("+ HTTP:")
        http_info = api_config.http
        logger.info("+   Request:")
        if http_info:
            if http_info.request:
                logger.info(f"+     HTTP method:  {http_info.request.method}")
                logger.info("+       Parameters:")
                for param in http_info.request.parameters:
                    logger.info(f"+         name:  {param.name}")
                    logger.info(f"+           required:  {param.required}")
                    logger.info(f"+           default value:  {param.default}")
                    logger.info(f"+           data type:  {param.value_type}")
                    logger.info(f"+           value format:  {param.value_format}")
            else:
                logger.info("+     Miss HTTP request settings.")
            logger.info("+     Response:")
            if http_info.response:
                logger.info(f"+       Values:  {http_info.response.value}")
            else:
                logger.info("+     Miss HTTP response settings.")
        else:
            logger.info("+     Miss HTTP settings.")


class DisplayAsYamlFormat(_BaseDisplayFormat):
    @property
    def format(self) -> Format:
        return Format.YAML

    def display(self, api_config: MockAPI) -> None:
        logger.info(api_config.format(self.format))


class DisplayAsJsonFormat(_BaseDisplayFormat):
    @property
    def format(self) -> Format:
        return Format.JSON

    def display(self, api_config: MockAPI) -> None:
        logger.info(api_config.format(self.format))
