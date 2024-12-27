from enum import Enum

Str_Resp_API: dict = {
    "url": "/test-str-resp",
    "http": {
        "request": {
            "method": "GET",
            "parameters": [
                {"name": "param1", "required": True, "type": "str"},
                {
                    "name": "id",
                    "required": True,
                    "type": "str",
                    "format": {
                        "strategy": "by_data_type",
                        "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                    },
                },
            ],
        },
        "response": {"strategy": "string", "value": "This is sample API as string value."},
    },
}

Json_Resp_API: dict = {
    "url": "/test-json-resp",
    "http": {
        "request": {"method": "GET", "parameters": [{"name": "param1", "required": True, "type": "str"}]},
        "response": {
            "strategy": "string",
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is sample API as JSON format '
            'value." }',
        },
    },
}

File_Content_Resp_Value: dict = {
    "url": "/test-file-content-resp",
    "http": {
        "request": {
            "method": "GET",
            "parameters": [
                {"name": "param1", "required": True, "type": "str"},
                {
                    "name": "fooType",
                    "required": True,
                    "type": "str",
                    "format": {"strategy": "from_enums", "enums": ["ENUM1", "ENUM2"]},
                },
            ],
        },
        "response": {"strategy": "file", "value": "youtube.json"},
    },
}

File_Content: dict = {
    "responseCode": "200",
    "errorMessage": "OK",
    "content": "This is sample API with response value from file content.",
}

Object_Content_Resp_Value: dict = {
    "url": "/test-object-resp",
    "http": {
        "request": {
            "method": "GET",
            "parameters": [
                {"name": "param1", "required": True, "type": "str"},
                {
                    "name": "date",
                    "required": True,
                    "type": "str",
                    "format": {
                        "strategy": "customize",
                        "customize": "datetime_value",
                        "variables": [{"name": "datetime_value", "value_format": "date-time"}],
                    },
                },
            ],
        },
        "response": {
            "strategy": "object",
            "properties": [
                {"name": "errorMessage", "required": True, "type": "str"},
                {"name": "responseCode", "required": True, "type": "str"},
                {
                    "name": "responseData",
                    "required": True,
                    "type": "list",
                    "items": [
                        {
                            "name": "id",
                            "required": True,
                            "type": "int",
                            "format": {
                                "strategy": "by_data_type",
                                "size": {"max": 9223372036854775807, "min": -9223372036854775808},
                            },
                        },
                        {"name": "name", "required": True, "type": "str"},
                        {"name": "value1", "required": True, "type": "str"},
                    ],
                },
            ],
        },
    },
}


class SampleType(Enum):
    ALL = "response_all"
    RESPONSE_AS_STR = "response_as_str"
    RESPONSE_AS_JSON = "response_as_json"
    RESPONSE_WITH_FILE = "response_with_file"
    RESPONSE_AS_OBJECT = "response_as_object"


Mocked_APIs: dict = {
    "base": {"url": "/test/v1"},
    "apis": {
        SampleType.RESPONSE_AS_STR.value: Str_Resp_API,
        SampleType.RESPONSE_AS_JSON.value: Json_Resp_API,
        SampleType.RESPONSE_WITH_FILE.value: File_Content_Resp_Value,
        SampleType.RESPONSE_AS_OBJECT.value: Object_Content_Resp_Value,
    },
}

Sample_Config_Value: dict = {
    "name": "Sample mock API",
    "description": "This is a sample config for the usage demonstration.",
    "mocked_apis": Mocked_APIs,
}


def get_sample_by_type(t: SampleType) -> dict:
    if t is SampleType.RESPONSE_AS_STR:
        return sample_config.response_as_str()
    elif t is SampleType.RESPONSE_AS_JSON:
        return sample_config.response_as_json()
    elif t is SampleType.RESPONSE_WITH_FILE:
        return sample_config.response_with_file()
    elif t is SampleType.RESPONSE_AS_OBJECT:
        return sample_config.response_as_object()
    elif t is SampleType.ALL:
        return sample_config.response()
    else:
        raise ValueError(f"It doesn't support the sample type {t}.")


class sample_config:
    @classmethod
    def response_as_str(cls) -> dict:
        return cls._config(
            name=SampleType.RESPONSE_AS_STR.value,
            response=Str_Resp_API,
        )

    @classmethod
    def response_as_json(cls) -> dict:
        return cls._config(
            name=SampleType.RESPONSE_AS_JSON.value,
            response=Json_Resp_API,
        )

    @classmethod
    def response_with_file(cls) -> dict:
        return cls._config(
            name=SampleType.RESPONSE_WITH_FILE.value,
            response=File_Content_Resp_Value,
        )

    @classmethod
    def response_as_object(cls) -> dict:
        return cls._config(
            name=SampleType.RESPONSE_AS_OBJECT.value,
            response=Object_Content_Resp_Value,
        )

    @classmethod
    def response(cls) -> dict:
        return Sample_Config_Value

    @classmethod
    def _config(cls, name: str, response: dict) -> dict:
        return {
            "name": "Sample mock API",
            "description": "This is a sample config for the usage demonstration.",
            "mocked_apis": {
                "base": {"url": "/test/v1"},
                "apis": {
                    name: response,
                },
            },
        }
