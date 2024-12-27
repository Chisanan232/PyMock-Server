import re

import pytest

from pymock_server.model import generate_empty_config
from pymock_server.model._sample import SampleType, get_sample_by_type


@pytest.mark.parametrize("st", SampleType)
def test_get_sample_by_valid_type(st: SampleType):
    sample_data = get_sample_by_type(st)
    mocked_apis_config = sample_data["mocked_apis"]["apis"]
    if st is SampleType.ALL:
        assert len(mocked_apis_config.keys()) == len(list(filter(lambda t: t is not SampleType.ALL, SampleType)))
        all_sample_types = list(filter(lambda t: t is not SampleType.ALL, SampleType))
        for sample_type in all_sample_types:
            assert sample_type.value in mocked_apis_config.keys()
    else:
        assert len(mocked_apis_config.keys()) == 1
        assert st.value in mocked_apis_config.keys()


@pytest.mark.parametrize("invalid_st", ["invalid_type"])
def test_get_sample_by_invalid_type(invalid_st: SampleType):
    with pytest.raises(ValueError) as exc_info:
        get_sample_by_type(invalid_st)
    assert re.search(r".{0,64}doesn't support.{0,64}" + re.escape(invalid_st), str(exc_info.value), re.IGNORECASE)


@pytest.mark.parametrize("st", SampleType)
def test_get_sample_is_correct_usage(st: SampleType):
    sample_data = get_sample_by_type(st)
    config_has_data = generate_empty_config().deserialize(sample_data)

    if st is SampleType.ALL:
        assert len(config_has_data.apis.apis.keys()) == len(list(filter(lambda t: t is not SampleType.ALL, SampleType)))
        all_sample_types = list(filter(lambda t: t is not SampleType.ALL, SampleType))
        for sample_type in all_sample_types:
            assert sample_type.value in config_has_data.apis.apis.keys()
    else:
        assert len(config_has_data.apis.apis.keys()) == 1
        assert st.value in config_has_data.apis.apis.keys()
