import importlib
import inspect
import os
import sys
from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional, Type, cast

from ...model import load_config
from ...model.api_config import MockAPI
from ...model.cmd_args import SubcmdGetArguments
from ..component import BaseSubCmdComponent


class SubCmdGetComponent(BaseSubCmdComponent):
    def process(self, args: SubcmdGetArguments) -> None:  # type: ignore[override]
        current_api_config = load_config(path=args.config_path)
        if current_api_config is None:
            print("❌  Empty content in configuration file.")
            sys.exit(1)
        apis_info = current_api_config.apis
        if apis_info is None:
            print("❌  Cannot find any API setting to mock.")
            sys.exit(1)
        specific_api_info = apis_info.get_api_config_by_url(url=args.api_path, base=apis_info.base)
        APIInfoDisplayChain().show(args, specific_api_info)
        # if specific_api_info:
        #     print("🍻  Find the API info which satisfy the conditions.")
        #     if args.show_detail:
        #         if args.show_as_format == "text":
        #             DisplayAsTextFormat().display(specific_api_info)
        #         elif args.show_as_format == "json":
        #             DisplayAsJsonFormat().display(specific_api_info)
        #         elif args.show_as_format == "yaml":
        #             DisplayAsYamlFormat().display(specific_api_info)
        #         else:
        #             print("❌  Invalid valid of option *--show-as-format*.")
        #             sys.exit(1)
        #     sys.exit(0)
        # else:
        #     print("🙅‍♂️  Cannot find the API info with the conditions.")
        #     sys.exit(1)


class _BaseDisplayChain(metaclass=ABCMeta):
    def __init__(self):
        self.displays: Dict[str, "_BaseDisplayFormat"] = self._get_display_members()
        print(f"[DEBUG] self.displays: {self.displays}")
        assert self.displays, "The API info display chain cannot be empty."
        self._current_format: str = "text"
        self._current_display = self.displays[self._current_format]

    def _get_display_members(self) -> Dict[str, "_BaseDisplayFormat"]:
        current_module = os.path.basename(__file__).replace(".py", "")
        module_path = ".".join([__package__, current_module])
        members = inspect.getmembers(
            object=importlib.import_module(module_path),
            predicate=lambda c: inspect.isclass(c) and issubclass(c, _BaseDisplayFormat) and not inspect.isabstract(c),
        )

        all_displays = {}
        for m in members:
            cls_obj = cast(_BaseDisplayFormat, m[1]())
            all_displays[cls_obj.format] = cls_obj

        return all_displays

    @property
    def current_display(self) -> "_BaseDisplayFormat":
        return self._current_display

    def next(self) -> "_BaseDisplayFormat":
        self._current_display = self.displays[self._current_format]
        return self._current_display

    def dispatch(self, format: str) -> "_BaseDisplayFormat":
        if format not in self.displays.keys():
            print("❌  Invalid valid of option *--show-as-format*.")
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
    def show(self, args: SubcmdGetArguments, specific_api_info: Optional[MockAPI]) -> None:
        if specific_api_info:
            print("🍻  Find the API info which satisfy the conditions.")
            if args.show_detail:
                self.dispatch(format=args.show_as_format).display(specific_api_info)
                # if args.show_as_format == "text":
                #     DisplayAsTextFormat().display(specific_api_info)
                # elif args.show_as_format == "json":
                #     DisplayAsJsonFormat().display(specific_api_info)
                # elif args.show_as_format == "yaml":
                #     DisplayAsYamlFormat().display(specific_api_info)
                # else:
                #     print("❌  Invalid valid of option *--show-as-format*.")
                #     sys.exit(1)
            sys.exit(0)
        else:
            print("🙅‍♂️  Cannot find the API info with the conditions.")
            sys.exit(1)


class _BaseDisplayFormat(metaclass=ABCMeta):
    @property
    @abstractmethod
    def format(self) -> str:
        pass

    def is_responsible(self, f: str) -> bool:
        return self.format == f

    @abstractmethod
    def display(self, specific_api_info: MockAPI) -> None:
        pass


class DisplayAsTextFormat(_BaseDisplayFormat):
    @property
    def format(self) -> str:
        return "text"

    def display(self, specific_api_info: MockAPI) -> None:
        print("+--------------- API info ---------------+")
        print(f"+ Path:  {specific_api_info.url}")
        print("+ HTTP:")
        http_info = specific_api_info.http
        print("+   Request:")
        if http_info:
            if http_info.request:
                print(f"+     HTTP method:  {http_info.request.method}")
                print("+       Parameters:")
                for param in http_info.request.parameters:
                    print(f"+         name:  {param.name}")
                    print(f"+           required:  {param.required}")
                    print(f"+           default value:  {param.default}")
                    print(f"+           data type:  {param.value_type}")
                    print(f"+           value format:  {param.value_format}")
            else:
                print("+     Miss HTTP request settings.")
            print("+     Response:")
            if http_info.response:
                print(f"+       Values:  {http_info.response.value}")
            else:
                print("+     Miss HTTP response settings.")
        else:
            print("+     Miss HTTP settings.")


class DisplayAsYamlFormat(_BaseDisplayFormat):
    @property
    def format(self) -> str:
        return "yaml"

    def display(self, specific_api_info: MockAPI) -> None:
        print(specific_api_info.format(self.format))


class DisplayAsJsonFormat(_BaseDisplayFormat):
    @property
    def format(self) -> str:
        return "json"

    def display(self, specific_api_info: MockAPI) -> None:
        print(specific_api_info.format(self.format))
