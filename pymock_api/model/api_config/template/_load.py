import fnmatch
import glob
import os
import pathlib
from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

from ...._utils import YAML
from ...._utils.file_opt import _BaseFileOperation
from ...enums import ConfigLoadingOrder, ConfigLoadingOrderKey, set_loading_function
from .._base import _Config
from . import TemplateConfig
from ._base import _BaseTemplatableConfig


class TemplateConfigOpts(metaclass=ABCMeta):
    _config_file_name: str = "api.yaml"

    def register_callbacks(self) -> "TemplateConfigOpts":
        return self

    @property
    def config_file_name(self) -> str:
        return self._config_file_name

    @config_file_name.setter
    def config_file_name(self, n: str) -> None:
        self._config_file_name = n

    @property
    @abstractmethod
    def _template_config(self) -> TemplateConfig:
        pass

    @property
    @abstractmethod
    def _config_file_format(self) -> str:
        pass

    @property
    @abstractmethod
    def _deserialize_as_template_config(self) -> "_BaseTemplatableConfig":
        pass

    @abstractmethod
    def _set_template_config(self, config: _Config, **kwargs) -> None:
        pass

    def _set_mocked_apis(self, api_key: str = "", api_config: Optional[_Config] = None) -> None:
        raise NotImplementedError


class _BaseTemplateConfigLoader:
    """The data model which could load template configuration."""

    _configuration: _BaseFileOperation = YAML()

    _template_config_opts: TemplateConfigOpts

    def register(self, template_config_ops: TemplateConfigOpts) -> None:
        self._template_config_opts = template_config_ops

    @abstractmethod
    def load_config(self, *args, **kwargs) -> None:
        pass

    def _deserialize_and_set_template_config(self, path: str) -> None:
        config = self._deserialize_template_config(path)
        assert config is not None, "Configuration should not be empty."
        args = {
            "path": path,
        }
        self._template_config_opts._set_template_config(config, **args)

    def _deserialize_template_config(self, path: str) -> Optional[_Config]:
        # Read YAML config
        yaml_config = self._configuration.read(path)
        # Deserialize YAML config content as PyMock data model
        config = self._template_config_opts._deserialize_as_template_config
        config.base_file_path = str(pathlib.Path(path).parent)
        config.config_path = pathlib.Path(path).name
        return config.deserialize(yaml_config)


class TemplateConfigLoaderWithAPIConfig(_BaseTemplateConfigLoader):
    def register(self, template_config_ops: TemplateConfigOpts) -> None:
        super().register(template_config_ops)
        set_loading_function(
            data_model_key=self._template_config_opts._config_file_format,
            apis=self.load_config,
        )

    def load_config(self, mocked_apis_data: dict) -> None:
        self._template_config_opts._set_mocked_apis()
        if mocked_apis_data:
            for mock_api_name in mocked_apis_data.keys():
                api_config = self._template_config_opts._deserialize_as_template_config
                api_config.config_path = f"{mock_api_name}{api_config.config_file_tail}.yaml"
                self._template_config_opts._set_mocked_apis(
                    api_key=mock_api_name,
                    api_config=api_config.deserialize(data=mocked_apis_data.get(mock_api_name, None)),
                )


class TemplateConfigLoaderByScanFile(_BaseTemplateConfigLoader):
    def register(self, template_config_ops: TemplateConfigOpts) -> None:
        super().register(template_config_ops)
        set_loading_function(
            data_model_key=self._template_config_opts._config_file_format,
            file=self.load_config,
        )

    def load_config(self) -> None:
        customize_config_file_format = "**"
        config_file_format = f"[!_**]{customize_config_file_format}"
        # all_paths = glob.glob(f"{self._base_path}**/[!_*]*.yaml", recursive=True)
        config_base_path = self._template_config_opts._template_config.values.base_file_path
        all_paths = glob.glob(str(pathlib.Path(config_base_path, config_file_format)))
        api_config_path = str(pathlib.Path(config_base_path, self._template_config_opts.config_file_name))
        if os.path.exists(api_config_path):
            all_paths.remove(api_config_path)
        for path in all_paths:
            if os.path.isdir(path):
                # Has tag as directory
                for path_with_tag in glob.glob(str(pathlib.Path(path, self._template_config_opts._config_file_format))):
                    # In the tag directory, it's config
                    self._deserialize_and_set_template_config(path_with_tag)
            else:
                assert os.path.isfile(path) is True
                if fnmatch.fnmatch(path, self._template_config_opts._config_file_format):
                    # Doesn't have tag, it's config
                    self._deserialize_and_set_template_config(path)


class TemplateConfigLoaderByApply(_BaseTemplateConfigLoader):
    def register(self, template_config_ops: TemplateConfigOpts) -> None:
        super().register(template_config_ops)
        set_loading_function(
            data_model_key=self._template_config_opts._config_file_format,
            apply=self.load_config,
        )

    def load_config(self) -> None:
        if self._template_config_opts._template_config.apply:
            apply_apis = self._template_config_opts._template_config.apply.api
            all_ele_is_dict = list(map(lambda e: isinstance(e, dict), apply_apis))
            config_path_format = self._template_config_opts._config_file_format
            config_base_path = self._template_config_opts._template_config.values.base_file_path
            if False in all_ele_is_dict:
                # no tag API
                for api in apply_apis:
                    assert isinstance(api, str)
                    api_config = config_path_format.replace("**", api)
                    config_path = str(pathlib.Path(config_base_path, api_config))
                    self._deserialize_and_set_template_config(config_path)
            else:
                # API with tag
                for tag_apis in apply_apis:
                    assert isinstance(tag_apis, dict)
                    for tag, apis in tag_apis.items():
                        for api in apis:
                            api_config = config_path_format.replace("**", api)
                            config_path = str(pathlib.Path(config_base_path, tag, api_config))
                            self._deserialize_and_set_template_config(config_path)


class TemplateConfigLoader(_BaseTemplateConfigLoader):
    """The layer for extending all the configuration loaders"""

    _loaders: Dict[str, "_BaseTemplateConfigLoader"] = {}

    def __init__(self):
        super().__init__()
        self._loaders: Dict[str, "_BaseTemplateConfigLoader"] = {
            ConfigLoadingOrderKey.APIs.value: TemplateConfigLoaderWithAPIConfig(),
            ConfigLoadingOrderKey.FILE.value: TemplateConfigLoaderByScanFile(),
            ConfigLoadingOrderKey.APPLY.value: TemplateConfigLoaderByApply(),
        }

    def register(self, template_config_ops: TemplateConfigOpts) -> None:
        super().register(template_config_ops)
        for loader in self._loaders.values():
            loader.register(template_config_ops)

    def load_config(self, mocked_apis_data: dict) -> None:
        loading_order = self._template_config_opts._template_config.load_config.order

        if self._template_config_opts._template_config.load_config.includes_apis:
            if (ConfigLoadingOrder.APIs not in loading_order) or (
                ConfigLoadingOrder.APIs in loading_order and not self._template_config_opts._template_config.activate
            ):
                self._loaders[ConfigLoadingOrderKey.APIs.value].load_config(mocked_apis_data)

        if self._template_config_opts._template_config.activate:
            for load_config in loading_order:
                args = (mocked_apis_data,)
                args = load_config.get_loading_function_args(*args)  # type: ignore[assignment]
                load_config.get_loading_function(data_modal_key=self._template_config_opts._config_file_format)(*args)


class TemplatableConfigLoadable(TemplateConfigOpts):
    _template_config_loader: Optional[_BaseTemplateConfigLoader] = None

    def initial_loadable_data_modal(self) -> None:
        self._template_config_loader = self.init_template_config_loader()
        self._template_config_loader.register(self.register_callbacks())

    def init_template_config_loader(self) -> _BaseTemplateConfigLoader:
        return TemplateConfigLoader()
