import re
from enum import Enum
from pydoc import locate
from typing import Any, Callable, Dict, Optional, Union

from pymock_api.model.openapi._js_handlers import convert_js_type


class Format(Enum):
    TEXT: str = "text"
    YAML: str = "yaml"
    JSON: str = "json"


class SampleType(Enum):
    ALL: str = "response_all"
    RESPONSE_AS_STR: str = "response_as_str"
    RESPONSE_AS_JSON: str = "response_as_json"
    RESPONSE_WITH_FILE: str = "response_with_file"


class ResponseStrategy(Enum):
    STRING: str = "string"
    FILE: str = "file"
    OBJECT: str = "object"

    @staticmethod
    def to_enum(v: Union[str, "ResponseStrategy"]) -> "ResponseStrategy":
        if isinstance(v, str):
            return ResponseStrategy(v.lower())
        else:
            return v

    def initial_response_data(self) -> Dict[str, Union["ResponseStrategy", list, dict]]:
        response_data: Dict[str, Union["ResponseStrategy", list, dict]] = {
            "strategy": self,
            # "data": None,
        }
        if self is ResponseStrategy.OBJECT:
            response_data["data"] = []
        else:
            response_data["data"] = {}
        return response_data

    def process_response_from_reference(
        self,
        init_response: dict,
        data: dict,
        get_schema_parser_factory: Callable,
        has_ref_callback: Callable,
        get_ref_callback: Callable,
    ) -> dict:
        response_schema_ref = get_ref_callback(data)
        parser = get_schema_parser_factory().object(response_schema_ref)
        response_schema_properties: Optional[dict] = parser.get_properties(default=None)
        if response_schema_properties:
            for k, v in response_schema_properties.items():
                if self is ResponseStrategy.OBJECT:
                    # response_data_prop = self._process_response_value(property_value=v, strategy=strategy)
                    response_data_prop = self.generate_response(
                        property_value=v,
                        get_schema_parser_factory=get_schema_parser_factory,
                        has_ref_callback=has_ref_callback,
                        get_ref_callback=get_ref_callback,
                    )
                    assert isinstance(response_data_prop, dict)
                    response_data_prop["name"] = k
                    response_data_prop["required"] = k in parser.get_required(default=[k])
                    assert isinstance(
                        init_response["data"], list
                    ), "The response data type must be *list* if its HTTP response strategy is object."
                    init_response["data"].append(response_data_prop)
                else:
                    assert isinstance(
                        init_response["data"], dict
                    ), "The response data type must be *dict* if its HTTP response strategy is not object."
                    # resp_data["data"][k] = self._process_response_value(property_value=v, strategy=strategy)
                    init_response["data"][k] = self.generate_response(
                        property_value=v,
                        get_schema_parser_factory=get_schema_parser_factory,
                        has_ref_callback=has_ref_callback,
                        get_ref_callback=get_ref_callback,
                    )
        return init_response

    def process_response_from_data(
        self,
        init_response: dict,
        data: dict,
        get_schema_parser_factory: Callable,
        has_ref_callback: Callable,
        get_ref_callback: Callable,
    ) -> dict:
        if self is ResponseStrategy.OBJECT:
            # response_data_prop = self._process_response_value(property_value=_data, strategy=strategy)
            response_data_prop = self.generate_response(
                property_value=data,
                get_schema_parser_factory=get_schema_parser_factory,
                has_ref_callback=has_ref_callback,
                get_ref_callback=get_ref_callback,
            )
            assert isinstance(response_data_prop, dict)
            assert isinstance(
                init_response["data"], list
            ), "The response data type must be *list* if its HTTP response strategy is object."
            init_response["data"].append(response_data_prop)
        else:
            assert isinstance(
                init_response["data"], dict
            ), "The response data type must be *dict* if its HTTP response strategy is not object."
            # resp_data["data"][0] = self._process_response_value(property_value=_data, strategy=strategy)
            init_response["data"][0] = self.generate_response(
                property_value=data,
                get_schema_parser_factory=get_schema_parser_factory,
                has_ref_callback=has_ref_callback,
                get_ref_callback=get_ref_callback,
            )
        return init_response

    def generate_response(
        self,
        property_value: dict,
        get_schema_parser_factory: Callable,
        has_ref_callback: Callable,
        get_ref_callback: Callable,
    ) -> Union[str, list, dict]:
        if not property_value:
            return self.generate_empty_response()
        if has_ref_callback(property_value):
            return self.generate_response_from_reference(get_ref_callback(property_value))
        else:
            return self.generate_response_from_data(
                resp_prop_data=property_value,
                get_schema_parser_factory=get_schema_parser_factory,
                get_ref_callback=get_ref_callback,
            )

    def generate_empty_response(self) -> Union[str, Dict[str, Any]]:
        if self is ResponseStrategy.OBJECT:
            return {
                "name": "",
                # TODO: Set the *required* property correctly
                "required": False,
                # TODO: Set the *type* property correctly
                "type": None,
                # TODO: Set the *format* property correctly
                "format": None,
                "items": [],
            }
        else:
            return "empty value"

    def generate_response_from_reference(self, ref_data: dict) -> Union[str, Dict[str, Any]]:
        if self is ResponseStrategy.OBJECT:
            return {
                "name": "",
                # TODO: Set the *required* property correctly
                "required": True,
                # TODO: Set the *type* property correctly
                "type": "file",
                # TODO: Set the *format* property correctly
                "format": None,
                "items": [],
                "FIXME": "Handle the reference",
            }
        else:
            return "FIXME: Handle the reference"

    def generate_response_from_data(
        self,
        resp_prop_data: dict,
        get_schema_parser_factory: Callable,
        # has_ref_callback: Callable,
        get_ref_callback: Callable,
    ) -> Union[str, list, dict]:

        def _handle_list_type_data(data: dict, noref_val_process_callback: Callable, response: dict = {}) -> dict:
            single_response = get_ref_callback(data["items"])
            parser = get_schema_parser_factory().object(single_response)
            single_response_properties = parser.get_properties(default={})
            if single_response_properties:
                for item_k, item_v in parser.get_properties().items():
                    # if has_ref_callback(item_v):
                    #     # TODO: Should consider the algorithm to handle nested reference case
                    #     print("[WARNING] Not implement yet ...")
                    #     response = ref_val_process_callback(item_k, item_v, response)
                    # else:
                    response = noref_val_process_callback(item_k, item_v, response)
                    # item_type = convert_js_type(item_v["type"])
                    # # TODO: Set the *required* property correctly
                    # item = {"name": item_k, "required": True, "type": item_type}
                    # assert isinstance(
                    #     response_data_prop["items"], list
                    # ), "The data type of property *items* must be *list*."
                    # response_data_prop["items"].append(item)
            return response

        def _handle_list_type_value_with_object_strategy(data: dict) -> dict:

            # def _ref_process_callback(item_k: str, item_v: dict, response_data_prop: dict) -> dict:
            #     # TODO: Should consider the algorithm to handle nested reference case
            #     print("[WARNING] Not implement yet ...")
            #     return response_data_prop

            def _noref_process_callback(item_k: str, item_v: dict, response_data_prop: dict) -> dict:
                item_type = convert_js_type(item_v["type"])
                # TODO: Set the *required* property correctly
                item = {"name": item_k, "required": True, "type": item_type}
                assert isinstance(
                    response_data_prop["items"], list
                ), "The data type of property *items* must be *list*."
                response_data_prop["items"].append(item)
                return response_data_prop

            response_data_prop = {
                "name": "",
                # TODO: Set the *required* property correctly
                "required": True,
                "type": v_type,
                # TODO: Set the *format* property correctly
                "format": None,
                "items": [],
            }
            response_data_prop = _handle_list_type_data(
                data=data,
                # ref_val_process_callback=_ref_process_callback,
                noref_val_process_callback=_noref_process_callback,
                response=response_data_prop,
            )

            # single_response = get_ref_callback(data["items"])
            # parser = get_schema_parser_factory().object(single_response)
            # single_response_properties = parser.get_properties(default={})
            # if single_response_properties:
            #     for item_k, item_v in parser.get_properties().items():
            #         if has_ref_callback(item_v):
            #             # TODO: Should consider the algorithm to handle nested reference case
            #             print("[WARNING] Not implement yet ...")
            #         else:
            #             item_type = convert_js_type(item_v["type"])
            #             # TODO: Set the *required* property correctly
            #             item = {"name": item_k, "required": True, "type": item_type}
            #             assert isinstance(
            #                 response_data_prop["items"], list
            #             ), "The data type of property *items* must be *list*."
            #             response_data_prop["items"].append(item)
            return response_data_prop

        def _handle_object_type_value_with_object_strategy(v_type: str) -> dict:
            # FIXME: handle the reference like object type
            return {
                "name": "",
                # TODO: Set the *required* property correctly
                "required": True,
                "type": v_type,
                # TODO: Set the *format* property correctly
                "format": None,
                "items": None,
            }

        def _handle_other_types_value_with_object_strategy(v_type: str) -> dict:
            return {
                "name": "",
                # TODO: Set the *required* property correctly
                "required": True,
                "type": v_type,
                # TODO: Set the *format* property correctly
                "format": None,
                "items": None,
            }

        def _handle_list_type_value_with_non_object_strategy(data: dict) -> list:

            # def _ref_process_callback(item_k: str, item_v: dict, response_data_prop: dict) -> dict:
            #     # TODO: Should consider the algorithm to handle nested reference case
            #     print("[WARNING] Not implement yet ...")
            #     return response_data_prop

            def _noref_process_callback(item_k: str, item_v: dict, item: dict) -> dict:
                item_type = convert_js_type(item_v["type"])
                if locate(item_type) is str:
                    # lowercase_letters = string.ascii_lowercase
                    # random_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
                    random_value = "random string value"
                elif locate(item_type) is int:
                    # random_value = int(
                    #     "".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
                    random_value = "random integer value"
                else:
                    raise NotImplementedError
                item[item_k] = random_value
                return item

            item_info: dict = {}
            item_info = _handle_list_type_data(
                data=data,
                # ref_val_process_callback=_ref_process_callback,
                noref_val_process_callback=_noref_process_callback,
                response=item_info,
            )

            # single_response = get_ref_callback(data["items"])
            # parser = get_schema_parser_factory().object(single_response)
            # item = {}
            # single_response_properties = parser.get_properties(default={})
            # if single_response_properties:
            #     for item_k, item_v in parser.get_properties().items():
            #         if has_ref_callback(item_v):
            #             # TODO: Should consider the algorithm to handle nested reference case
            #             obj_item_type = convert_js_type(item_v["additionalProperties"]["type"])
            #             print("[WARNING] Not implement yet ...")
            #         else:
            #             item_type = convert_js_type(item_v["type"])
            #             if locate(item_type) is str:
            #                 # lowercase_letters = string.ascii_lowercase
            #                 # random_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
            #                 random_value = "random string value"
            #             elif locate(item_type) is int:
            #                 # random_value = int(
            #                 #     "".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
            #                 random_value = "random integer value"
            #             else:
            #                 raise NotImplementedError
            #             item[item_k] = random_value
            return [item_info]

        def _handle_each_data_types_response_with_object_strategy(data: dict, v_type: str) -> dict:
            if locate(v_type) == list:
                return _handle_list_type_value_with_object_strategy(data)
            elif locate(v_type) == dict:
                return _handle_object_type_value_with_object_strategy(v_type)
            else:
                return _handle_other_types_value_with_object_strategy(v_type)

        def _handle_each_data_types_response_with_non_object_strategy(
            resp_prop_data: dict, v_type: str
        ) -> Union[str, list]:
            if locate(v_type) == list:
                return _handle_list_type_value_with_non_object_strategy(resp_prop_data)
            elif locate(v_type) == dict:
                # FIXME: handle the reference like object type
                return "random object value"
            elif locate(v_type) == str:
                # lowercase_letters = string.ascii_lowercase
                # k_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
                return "random string value"
            elif locate(v_type) == int:
                # k_value = int("".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
                return "random integer value"
            elif locate(v_type) == bool:
                return "random boolean value"
            elif v_type == "file":
                # TODO: Handle the file download feature
                return "random file output stream"
            else:
                raise NotImplementedError

        print(f"[DEBUG in _handle_not_ref_data] resp_prop_data: {resp_prop_data}")
        v_type = convert_js_type(resp_prop_data["type"])
        if self is ResponseStrategy.OBJECT:
            return _handle_each_data_types_response_with_object_strategy(resp_prop_data, v_type)
            # if locate(v_type) == list:
            #     return _handle_list_type_value_with_object_strategy(resp_prop_data)
            # elif locate(v_type) == dict:
            #     return _handle_object_type_value_with_object_strategy(v_type)
            # else:
            #     return _handle_other_types_value_with_object_strategy(v_type)
        else:
            return _handle_each_data_types_response_with_non_object_strategy(resp_prop_data, v_type)
            # if locate(v_type) == list:
            #     return _handle_list_type_value_with_non_object_strategy(resp_prop_data)
            # elif locate(v_type) == dict:
            #     # FIXME: handle the reference like object type
            #     return "random object value"
            # elif locate(v_type) == str:
            #     # lowercase_letters = string.ascii_lowercase
            #     # k_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
            #     return "random string value"
            # elif locate(v_type) == int:
            #     # k_value = int("".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
            #     return "random integer value"
            # elif locate(v_type) == bool:
            #     return "random boolean value"
            # elif v_type == "file":
            #     # TODO: Handle the file download feature
            #     return "random file output stream"
            # else:
            #     raise NotImplementedError


class ConfigLoadingOrderKey(Enum):
    APIs: str = "apis"
    APPLY: str = "apply"
    FILE: str = "file"


"""
Data structure sample:
{
    "MockAPI": {
        ConfigLoadingOrderKey.APIs.value: <Callable at memory xxxxa>,
        ConfigLoadingOrderKey.APPLY.value: <Callable at memory xxxxb>,
        ConfigLoadingOrderKey.FILE.value: <Callable at memory xxxxc>,
    },
    "HTTP": {
        ConfigLoadingOrderKey.APIs.value: <Callable at memory xxxxd>,
        ConfigLoadingOrderKey.APPLY.value: <Callable at memory xxxxe>,
        ConfigLoadingOrderKey.FILE.value: <Callable at memory xxxxf>,
    },
}
"""
ConfigLoadingFunction: Dict[str, Dict[str, Callable]] = {}


def set_loading_function(data_model_key: str, **kwargs) -> None:
    global ConfigLoadingFunction
    if False in [str(k).lower() in [str(o.value).lower() for o in ConfigLoadingOrder] for k in kwargs.keys()]:
        raise KeyError("The arguments only have *apis*, *file* and *apply* for setting loading function data.")
    if data_model_key not in ConfigLoadingFunction.keys():
        ConfigLoadingFunction[data_model_key] = {}
    ConfigLoadingFunction[data_model_key].update(**kwargs)


class ConfigLoadingOrder(Enum):
    APIs: str = ConfigLoadingOrderKey.APIs.value
    APPLY: str = ConfigLoadingOrderKey.APPLY.value
    FILE: str = ConfigLoadingOrderKey.FILE.value

    @staticmethod
    def to_enum(v: Union[str, "ConfigLoadingOrder"]) -> "ConfigLoadingOrder":
        if isinstance(v, str):
            return ConfigLoadingOrder(v.lower())
        else:
            return v

    def get_loading_function(self, data_modal_key: str) -> Callable:
        return ConfigLoadingFunction[data_modal_key][self.value]

    def get_loading_function_args(self, *args) -> Optional[tuple]:
        if self is ConfigLoadingOrder.APIs:
            if args:
                return args
        return ()


class OpenAPIVersion(Enum):
    V2: str = "OpenAPI V2"
    V3: str = "OpenAPI V3"

    @staticmethod
    def to_enum(v: Union[str, "OpenAPIVersion"]) -> "OpenAPIVersion":
        if isinstance(v, str):
            if re.search(r"OpenAPI V[2-3]", v):
                return OpenAPIVersion(v)
            if re.search(r"2\.\d(\.\d)?.{0,8}", v):
                return OpenAPIVersion.V2
            if re.search(r"3\.\d(\.\d)?.{0,8}", v):
                return OpenAPIVersion.V3
            raise NotImplementedError(f"PyMock-API doesn't support parsing OpenAPI configuration with version '{v}'.")
        else:
            return v
