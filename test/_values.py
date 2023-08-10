from collections import namedtuple
from typing import Dict, List
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


_Config_Name: str = "pytest name"
_Config_Description: str = "pytest description"
_Base_URL: str = "/api/v1/test"
_Test_URL: str = "/test-url"
_Test_HTTP_Method: str = "GET"
_Test_HTTP_Resp: str = "This is HTTP response for PyTest."
_Mock_APIs: dict = {
    "test_api_1": Mock(),
    "test_api_2": Mock(),
}
_Mock_API_HTTP: dict = {
    "request": Mock,
    "response": Mock,
}

# Sample API parameters
_Test_API_Parameter: dict = {
    "name": "param1",
    "required": True,
    "default": None,
    "type": "str",
    "format": "any_format",
}
_Test_API_Parameter_With_Int: dict = {
    "name": "param2",
    "required": False,
    "default": 0,
    "type": "int",
    "format": None,
}
_Test_API_Parameter_With_Str: dict = {
    "name": "param3",
    "required": False,
    "default": "default_value",
    "type": "str",
    "format": None,
}
_Test_API_Parameter_Without_Default: dict = {
    "name": "param4",
    "required": False,
    "default": None,
    "type": "dict",
    "format": None,
}
_Test_API_Parameters: List[dict] = [
    _Test_API_Parameter,
    _Test_API_Parameter_With_Int,
    _Test_API_Parameter_With_Str,
    _Test_API_Parameter_Without_Default,
]

# Sample API for testing ('<base URL>/google' with GET)
_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "GET",
            "parameters": _Test_API_Parameters,
        },
        "response": {"value": "This is Google home API."},
    },
}

# Sample API for testing ('<base URL>/test' with POST)
_Test_Home: dict = {
    "url": "/test",
    "http": {
        "request": {
            "method": "POST",
            "parameters": [_Test_API_Parameter],
        },
        "response": {"value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }'},
    },
    "cookie": [{"TEST": "cookie_value"}],
}

# Sample API for testing ('<base URL>/test' with PUT)
_YouTube_Home_Value: dict = {
    "url": "/youtube",
    "http": {
        "request": {
            "method": "PUT",
        },
        "response": {"value": "youtube.json"},
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}

_YouTube_API_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}


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


# Sample configuration content
class _TestConfig:
    Request: dict = {"method": "GET", "parameters": [_Test_API_Parameter]}
    Response: Dict[str, str] = {"value": _Test_HTTP_Resp}
    Http: dict = {"request": Request, "response": Response}
    Mock_API: dict = {"url": _Test_URL, "http": Http}
    Base: dict = {"url": _Base_URL}
    Mock_APIs: dict = {"base": Base, "test_config": Mock_API}
    API_Config: dict = {
        "name": _Config_Name,
        "description": _Config_Description,
        "mocked_apis": Mock_APIs,
    }


# For testing data objects in *.server.sgi._model*
_Test_Entry_Point: str = "entry-point"

_Cmd_Option = namedtuple("_Cmd_Option", ["option_name", "value"])
_Bind_Host_And_Port: _Cmd_Option = _Cmd_Option(option_name="--bind", value="127.0.0.1:9672")
_Workers_Amount: _Cmd_Option = _Cmd_Option(option_name="--workers", value=3)
_Log_Level: _Cmd_Option = _Cmd_Option(option_name="--log-level", value="info")

# Test command line options
_Test_SubCommand_Run: str = "run"
_Test_Config: str = "test-api.yaml"
_Test_Auto_Type: str = "auto"
_Test_App_Type: str = "flask"
_Test_FastAPI_App_Type: str = "fastapi"

# Test subcommand *config* options
_Test_SubCommand_Add: str = "add"

# Test subcommand *check* options
_Test_SubCommand_Check: str = "check"

# Test subcommand *inspect* options
_Test_SubCommand_Get: str = "get"
_Swagger_API_Document_URL: str = "Swagger API document URL"
_Cmd_Arg_API_Path: str = "/foo-home"
_Cmd_Arg_HTTP_Method: str = "GET"
_Show_Detail_As_Format: str = "text"

# Test subcommand *config* options
_Test_SubCommand_Sample: str = "sample"
_Generate_Sample: bool = True
_Print_Sample: bool = True
_Sample_File_Path: str = "pytest-api.yaml"
_Sample_Data_Type: str = "all"

# Test subcommand *config* options
_Test_SubCommand_Pull: str = "pull"
_API_Doc_Source: str = "127.0.0.1:8080"
