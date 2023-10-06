from collections import namedtuple
from typing import Dict, List
from unittest.mock import Mock

from pymock_api.model.enums import ResponseStrategy, TemplateApplyScanStrategy


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


def generate_mock_template(tail_naming: str = "") -> dict:
    return {
        "base_file_path": "./",
        "config_path": "",
        "config_path_format": "**.yaml" if not tail_naming else ("**" + f"-{tail_naming}" + ".yaml"),
    }


_Mock_Template_API_Setting: dict = generate_mock_template("api")
_Mock_Template_API_Request_Setting: dict = generate_mock_template("request")
_Mock_Template_API_Response_Setting: dict = generate_mock_template("response")

_Mock_Template_Values_Setting: dict = {
    "api": _Mock_Template_API_Setting,
    "request": _Mock_Template_API_Request_Setting,
    "response": _Mock_Template_API_Response_Setting,
}

_Mock_Template_Apply_Scan_Strategy: TemplateApplyScanStrategy = TemplateApplyScanStrategy.FILE_NAME_FIRST

_Mock_Template_Apply_Has_Tag_Setting: dict = {
    "scan_strategy": _Mock_Template_Apply_Scan_Strategy.value,
    "api": [
        {"foo": ["get_foo", "put_foo"]},
        {"foo-boo": ["get_foo-boo_export"]},
    ],
}

_Mock_Template_Apply_No_Tag_Setting: dict = {
    "scan_strategy": _Mock_Template_Apply_Scan_Strategy.value,
    "api": ["get_foo", "put_foo"],
}


def generate_template_apply(scan_strategy: str, api: List) -> dict:
    return {
        "scan_strategy": scan_strategy,
        "api": api,
    }


_Mock_Template_Config_Activate: bool = False

_Mock_Template_Setting: dict = {
    "activate": _Mock_Template_Config_Activate,
    "values": _Mock_Template_Values_Setting,
    "apply": _Mock_Template_Apply_Has_Tag_Setting,
}

_Mock_Templatable_Setting: dict = {
    "apply_template_props": False,
}


# Sample item of iterator
_Test_Iterable_Parameter_Item_Name: dict = {
    "name": "name",
    "required": True,
    "type": "str",
}
_Test_Iterable_Parameter_Item_Value: dict = {
    "name": "value",
    "required": True,
    "type": "str",
}
_Test_Iterable_Parameter_Items: List[dict] = [_Test_Iterable_Parameter_Item_Name, _Test_Iterable_Parameter_Item_Value]
_Test_Iterable_Parameter_With_Single_Value: dict = {
    "name": "single_iterable_param",
    "required": True,
    "default": None,
    "type": "list",
    "format": None,
    "items": [_Test_Iterable_Parameter_Item_Name],
}
_Test_Iterable_Parameter_With_MultiValue: dict = {
    "name": "iterable_param",
    "required": True,
    "default": None,
    "type": "list",
    "format": None,
    "items": _Test_Iterable_Parameter_Items,
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

# Test HTTP response
_General_String_Value: str = "This is test message for PyTest."
_Json_File_Name: str = "test.json"
_Json_File_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}
_Not_Exist_File_Name: str = "not_exist.json"
_Not_Json_File_Name: str = "test.yaml"
_Unexpected_File_Name: str = ".file"

_Test_Response_Property_Int: dict = {
    "name": "id",
    "required": True,
    "type": "int",
    "format": None,
}
_Test_Response_Property_Str: dict = {
    "name": "name",
    "required": True,
    "type": "str",
    "format": None,
}
_Test_Response_Property_List: dict = {
    "name": "keys",
    "required": False,
    "type": "list",
    "format": None,
    "items": _Test_Iterable_Parameter_Items,
}
_Test_Response_Properties: List[dict] = [
    _Test_Response_Property_Int,
    _Test_Response_Property_Str,
    _Test_Response_Property_List,
]


def _api_params(iterable_param_type: str) -> List[dict]:
    params = _Test_API_Parameters.copy()
    if iterable_param_type == "single":
        params.append(_Test_Iterable_Parameter_With_Single_Value)
        return params
    elif iterable_param_type == "multiple":
        params.append(_Test_Iterable_Parameter_With_MultiValue)
        return params
    else:
        raise TypeError


# Sample API for testing ('<base URL>/google' with GET)
_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "GET",
            "parameters": _api_params("single"),
        },
        "response": {
            "strategy": "string",
            "value": "This is Google home API.",
        },
    },
}

_Post_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "POST",
            "parameters": _api_params("multiple"),
        },
        "response": {
            "strategy": "string",
            "value": "This is Google home API with POST method.",
        },
    },
}

_Put_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "PUT",
            "parameters": [_Test_API_Parameter],
        },
        "response": {
            "strategy": "string",
            "value": "Change something successfully.",
        },
    },
}

_Delete_Google_Home_Value: dict = {
    "url": "/google",
    "http": {
        "request": {
            "method": "DELETE",
        },
        "response": {
            "strategy": "string",
            "value": "Delete successfully.",
        },
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
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is Test home." }',
        },
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
        "response": {
            "strategy": "file",
            "path": "youtube.json",
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}

_YouTube_API_Content: dict = {"responseCode": "200", "errorMessage": "OK", "content": "This is YouTube home."}

# Sample API for testing ('<base URL>/test' with POST and object type strategy of HTTP response)
_HTTP_Response_Properties_With_Object_Strategy = [
    {
        "name": "id",
        "required": True,
        "type": "int",
        "format": None,
    },
    {
        "name": "role",
        "required": True,
        "type": "str",
        "format": None,
    },
    {
        "name": "details",
        "required": False,
        "type": "list",
        "format": None,
        "items": [
            {
                "name": "name",
                "required": True,
                "type": "str",
            },
            {
                "name": "level",
                "required": True,
                "type": "int",
            },
            {
                "name": "key",
                "required": True,
                "type": "str",
            },
        ],
    },
]
_Foo_Object_Value: dict = {
    "url": "/foo-object",
    "http": {
        "request": {
            "method": "POST",
        },
        "response": {
            "strategy": "object",
            "properties": _HTTP_Response_Properties_With_Object_Strategy,
        },
    },
    "cookie": [{"USERNAME": "test"}, {"SESSION_EXPIRED": "2023-12-31T00:00:00.000"}],
}


_Mocked_APIs: dict = {
    "template": _Mock_Template_Setting,
    "base": {"url": _Base_URL},
    "apis": {
        "google_home": _Google_Home_Value,
        "post_google_home": _Post_Google_Home_Value,
        "put_google_home": _Put_Google_Home_Value,
        "delete_google_home": _Delete_Google_Home_Value,
        "test_home": _Test_Home,
        "youtube_home": _YouTube_Home_Value,
        "foo_object": _Foo_Object_Value,
    },
}

_Test_Config_Value: dict = {
    "name": "Test mocked API",
    "description": "This is a test for the usage demonstration.",
    "auth_cookie": [{"USERNAME": "test"}, {"PASSWORD": "test"}],
    "mocked_apis": _Mocked_APIs,
}

_Test_Tag: str = "pytest-mocked-api"


# Sample configuration content
class _TestConfig:
    Request: dict = {"method": "GET", "parameters": [_Test_API_Parameter]}
    Response: Dict[str, str] = {"strategy": "string", "value": _Test_HTTP_Resp}
    Http: dict = {"request": Request, "response": Response}
    Mock_API: dict = {"url": _Test_URL, "http": Http, "tag": _Test_Tag}
    Base: dict = {"url": _Base_URL}
    Mock_APIs: dict = {
        "template": _Mock_Template_Setting,
        "base": Base,
        "apis": {
            "test_config": Mock_API,
        },
    }
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

# Test subcommand *add* options
_Test_SubCommand_Add: str = "add"
_Test_Response_Strategy: ResponseStrategy = ResponseStrategy.STRING

# Test subcommand *check* options
_Test_SubCommand_Check: str = "check"

# Test subcommand *inspect* options
_Test_SubCommand_Get: str = "get"
_Swagger_API_Document_URL: str = "Swagger API document URL"
_Cmd_Arg_API_Path: str = "/foo-home"
_Cmd_Arg_HTTP_Method: str = "GET"
_Show_Detail_As_Format: str = "text"

# Test subcommand *sample* options
_Test_SubCommand_Sample: str = "sample"
_Generate_Sample: bool = True
_Print_Sample: bool = True
_Sample_File_Path: str = "pytest-api.yaml"
_Sample_Data_Type: str = "all"

# Test subcommand *pull* options
_Test_SubCommand_Pull: str = "pull"
_API_Doc_Source: str = "127.0.0.1:8080"
