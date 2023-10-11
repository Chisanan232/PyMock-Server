import re

import pytest

from pymock_api.model.enums import set_loading_function


def test_set_loading_function():
    with pytest.raises(KeyError) as exc_info:
        set_loading_function(invalid_arg="any value")
    assert re.search(
        r"The arguments only have \*apis\*, \*file\* and \*apply\*.{0,64}", str(exc_info.value), re.IGNORECASE
    )
