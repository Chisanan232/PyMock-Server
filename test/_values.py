from unittest.mock import Mock


class APIConfigValue:
    @property
    def name(self) -> str:
        return "pytest-mocked-api"

    @property
    def description(self) -> str:
        return "This is mock api config data object for PyTest."

    @property
    def apis(self) -> dict:
        return _Mock_APIs


_Base_URL: str = "/test/v1"
_Test_URL: str = "/test-url"
_Test_HTTP_Method: str = "GET"
_Test_HTTP_Req_Params: dict = {"param1": "val1", "param2": "val2"}
_Test_HTTP_Resp: str = "This is HTTP response for PyTest."
_Mock_APIs: dict = {
    "test_api_1": Mock(),
    "test_api_2": Mock(),
}
_Mock_API_HTTP: dict = {
    "request": Mock,
    "response": Mock,
}

_YouTube_Home_Value: dict = {
    "url": "/youtube",
    "http": {"request": {"method": "GET", "parameters": [{"param1": "val1"}]}, "response": {"value": "youtube.json"}},
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}

_YouTube_API_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}

_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {"method": "GET", "parameters": [{"param1": "val1"}]},
        "response": {"value": "This is Google home API."},
    },
}

_Test_Home: dict = {
    "url": "/test",
    "http": {
        "request": {"method": "GET", "parameters": [{"param1": "val1"}]},
        "response": {"value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }'},
    },
    "cookie": [{"TEST": "cookie_value"}],
}

_Mocked_APIs: dict = {
    "base": {"url": "/test/v1"},
    "google_home": _Google_Home_Value,
    "test_home": _Test_Home,
    "youtube_home": _YouTube_Home_Value,
}

_Test_Config_Value: dict = {
    "name": "Test mocked API",
    "description": "This is a test for the usage demonstration.",
    "auth_cookie": [{"USERNAME": "test"}, {"PASSWORD": "test"}],
    "mocked_apis": _Mocked_APIs,
}
