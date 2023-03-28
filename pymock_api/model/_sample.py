Str_Resp_API: dict = {
    "url": "/test-str-resp",
    "http": {
        "request": {"method": "GET", "parameters": [{"param1": "val1"}]},
        "response": {"value": "This is sample API as string value."},
    },
}

Json_Resp_API: dict = {
    "url": "/test-json-resp",
    "http": {
        "request": {"method": "GET", "parameters": [{"param1": "val1"}]},
        "response": {
            "value": '{ "responseCode": "200", "errorMessage": "OK", "content": "This is sample API as JSON format '
            'value." }'
        },
    },
}

File_Content_Resp_Value: dict = {
    "url": "/test-file-content-resp",
    "http": {"request": {"method": "GET", "parameters": [{"param1": "val1"}]}, "response": {"value": "youtube.json"}},
}

File_Content: dict = {
    "responseCode": "200",
    "errorMessage": "OK",
    "content": "This is sample API with response value from file content.",
}

Mocked_APIs: dict = {
    "base": {"url": "/test/v1"},
    "str_response": Str_Resp_API,
    "json_response": Json_Resp_API,
    "file_content_response": File_Content_Resp_Value,
}

Sample_Config_Value: dict = {
    "name": "Sample mock API",
    "description": "This is a sample config for the usage demonstration.",
    "mocked_apis": Mocked_APIs,
}


class sample_config:
    @classmethod
    def response_as_str(cls) -> dict:
        return cls._config(
            name="str_response",
            response=Str_Resp_API,
        )

    @classmethod
    def response_as_json(cls) -> dict:
        return cls._config(
            name="json_response",
            response=Json_Resp_API,
        )

    @classmethod
    def response_with_file(cls) -> dict:
        return cls._config(
            name="file_content_response",
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
