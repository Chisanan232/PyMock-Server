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
