from typing import List

import pytest

from fake_api_server.model.api_config import (
    FakeAPIConfig,
    TemplatableConfigLoadable,
    _BaseTemplateConfigLoader,
)
from fake_api_server.model.api_config.template._load.process import TemplateConfigOpts

# isort: off
from test.unit_test.model.api_config.template._test_case import (
    DeserializeAPIConfigFromYamlTestCaseFactory as test_case_factory,
)

# isort: on

test_case_factory.load()
_Test_Data: List[str] = test_case_factory.get_test_case()


@pytest.fixture(scope="function")
def api_config() -> FakeAPIConfig:
    return FakeAPIConfig()


@pytest.mark.parametrize("api_config_yaml_path", _Test_Data)
def test_loader_independent(api_config: FakeAPIConfig, api_config_yaml_path: str):

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
