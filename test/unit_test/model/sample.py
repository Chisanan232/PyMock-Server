import re

import pytest

from pymock_server.model._sample import SampleType, get_sample_by_type


@pytest.mark.parametrize("st", SampleType)
def test_get_sample_by_valid_type(st: SampleType):
    base_config_number: int = 1
    sample_data = get_sample_by_type(st)
    if st is SampleType.ALL:
        assert len(sample_data["mocked_apis"].keys()) == 3 + base_config_number
        all_sample_types = list(filter(lambda t: t is not SampleType.ALL, SampleType))
        for sample_type in all_sample_types:
            assert sample_type.value in sample_data["mocked_apis"].keys()
    else:
        assert len(sample_data["mocked_apis"].keys()) == 1 + base_config_number
        assert st.value in sample_data["mocked_apis"].keys()


@pytest.mark.parametrize("invalid_st", ["invalid_type"])
def test_get_sample_by_invalid_type(invalid_st: SampleType):
    with pytest.raises(ValueError) as exc_info:
        get_sample_by_type(invalid_st)
    assert re.search(r".{0,64}doesn't support.{0,64}" + re.escape(invalid_st), str(exc_info.value), re.IGNORECASE)
