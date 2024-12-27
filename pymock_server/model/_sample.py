from enum import Enum

Str_Resp_API: dict = {
    "url": "/test-str-resp",
    "http": {
        "request": {"method": "GET", "parameters": [{"param1": "val1", "required": True, "type": "str"}]},
        "response": {"strategy": "string", "value": "This is sample API as string value."},
    },
}

Json_Resp_API: dict = {
    "url": "/test-json-resp",
    "http": {
        "request": {"method": "GET", "parameters": [{"param1": "val1", "required": True, "type": "str"}]},
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
        "request": {"method": "GET", "parameters": [{"param1": "val1", "required": True, "type": "str"}]},
        "response": {"strategy": "file", "value": "youtube.json"},
    },
}

File_Content: dict = {
    "responseCode": "200",
    "errorMessage": "OK",
    "content": "This is sample API with response value from file content.",
}


class SampleType(Enum):
    ALL = "response_all"
    RESPONSE_AS_STR = "response_as_str"
    RESPONSE_AS_JSON = "response_as_json"
    RESPONSE_WITH_FILE = "response_with_file"


Mocked_APIs: dict = {
    "base": {"url": "/test/v1"},
    SampleType.RESPONSE_AS_STR.value: Str_Resp_API,
    SampleType.RESPONSE_AS_JSON.value: Json_Resp_API,
    SampleType.RESPONSE_WITH_FILE.value: File_Content_Resp_Value,
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
    def response(cls) -> dict:
        return Sample_Config_Value

    @classmethod
    def _config(cls, name: str, response: dict) -> dict:
        return {
            "name": "Sample mock API",
            "description": "This is a sample config for the usage demonstration.",
            "mocked_apis": {
                "base": {"url": "/test/v1"},
                name: response,
            },
        }
