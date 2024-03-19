import glob
import os
import pathlib
from typing import List

import pytest

from pymock_api.model.api_config import APIConfig
from pymock_api.model.api_config.template._load import (
    TemplatableConfigLoadable,
    TemplateConfigOpts,
    _BaseTemplateConfigLoader,
)

# _Test_Data: str = "./test/data/check_test/data_model/entire_api/valid/has-base-info_and_tags.yaml"
_Test_Data: List[str] = []
yaml_dir = os.path.join(
    str(pathlib.Path(__file__).parent.parent.parent.parent.parent),
    "data",
    "check_test",
    "data_model",
    "entire_api",
    "valid",
    "*.yaml",
)
for yaml_config_path in glob.glob(yaml_dir):
    _Test_Data.append(yaml_config_path)


@pytest.fixture(scope="function")
def api_config() -> APIConfig:
    return APIConfig()


@pytest.mark.parametrize("api_config_yaml_path", _Test_Data)
def test_loader_independent(api_config: APIConfig, api_config_yaml_path: str):

    def get_template_config_opts_id(_data_modal: TemplatableConfigLoadable) -> int:
        assert hasattr(_data_modal, "_template_config_loader")
        assert isinstance(_data_modal._template_config_loader, _BaseTemplateConfigLoader)

        assert hasattr(_data_modal._template_config_loader, "_template_config_opts")
        assert isinstance(_data_modal._template_config_loader._template_config_opts, TemplateConfigOpts)

        return id(_data_modal._template_config_loader._template_config_opts)

    # Deserialize a data modal *APIConfig*
    api_config_data_modal = api_config.from_yaml(path=api_config_yaml_path)

    # Try to get other data modals which is templatable
    # Verify their loader should include different instance of object *TemplateConfigOpts*
    mocked_apis_modal = api_config_data_modal.apis
    all_mocked_apis = mocked_apis_modal.apis
    for key, api_modal in all_mocked_apis.items():
        http_modal = api_modal.http

        # Verify the data type
        assert isinstance(mocked_apis_modal, TemplatableConfigLoadable)
        assert isinstance(api_modal, TemplatableConfigLoadable)
        assert isinstance(http_modal, TemplatableConfigLoadable)
        # Verify the instance of template configuration operations
        assert (
            get_template_config_opts_id(mocked_apis_modal)
            != get_template_config_opts_id(api_modal)
            != get_template_config_opts_id(http_modal)
        )
