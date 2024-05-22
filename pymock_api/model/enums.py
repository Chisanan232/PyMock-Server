import re
from collections import namedtuple
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


_PropertyDefaultRequired = namedtuple("_PropertyDefaultRequired", ("empty", "general"))
_Default_Required: _PropertyDefaultRequired = _PropertyDefaultRequired(empty=False, general=True)


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
        parse_from_schema: bool = True,
    ) -> dict:
        if parse_from_schema:
            response_schema_ref = get_schema_parser_factory().reference_object().get_schema_ref(data)
        else:
            response_schema_ref = data
        print(f"[DEBUG in process_response_from_reference] data: {data}")
        return self._process_reference_object(init_response, response_schema_ref, get_schema_parser_factory)

    def _process_reference_object(
        self,
        init_response: dict,
        response_schema_ref: dict,
        get_schema_parser_factory: Callable,
        empty_body_key: str = "",
        not_set_init_resp: bool = False,
    ) -> dict:
        parser = get_schema_parser_factory().object(response_schema_ref)
        response_schema_properties: Optional[dict] = parser.get_properties(default={})
        print(f"[DEBUG in process_response_from_reference] response_schema_ref: {response_schema_ref}")
        print(f"[DEBUG in process_response_from_reference] response_schema_properties: {response_schema_properties}")
        if response_schema_properties:
            for k, v in response_schema_properties.items():
                print(f"[DEBUG in process_response_from_reference] k: {k}")
                print(f"[DEBUG in process_response_from_reference] v: {v}")
                # Check reference again
                if get_schema_parser_factory().reference_object().has_ref(v):
                    response_config = self._process_reference_object(
                        init_response=self.initial_response_data(),
                        response_schema_ref=get_schema_parser_factory().reference_object().get_schema_ref(v),
                        get_schema_parser_factory=get_schema_parser_factory,
                        empty_body_key=k,
                    )
                    if self is ResponseStrategy.OBJECT:
                        print(
                            f"[DEBUG in process_response_from_reference] before asserion, response_config: {response_config}"
                        )
                        response_config = response_config["data"][0]
                    else:
                        response_config = response_config["data"][k]
                else:
                    response_config = self._generate_response(  # type: ignore[assignment]
                        init_response=init_response,
                        property_value=v,
                        get_schema_parser_factory=get_schema_parser_factory,
                        property_key=k,
                    )
                print(f"[DEBUG in process_response_from_reference] response_config: {response_config}")
                if self is ResponseStrategy.OBJECT:
                    response_data_prop = self._ensure_data_structure_when_object_strategy(
                        init_response, response_config
                    )
                    print(f"[DEBUG in process_response_from_reference] response_data_prop: {response_data_prop}")
                    response_data_prop["name"] = k
                    response_data_prop["required"] = k in parser.get_required(default=[k])
                    init_response["data"].append(response_data_prop)
                else:
                    self._ensure_data_structure_when_non_object_strategy(init_response)
                    init_response["data"][k] = response_config
            print(f"[DEBUG in process_response_from_reference] parse with body, init_response: {init_response}")
            return init_response
        else:
            # The section which doesn't have setting body
            # response_config = self._generate_response(
            #     init_response=init_response,
            #     property_value={},  # It's {}
            #     get_schema_parser_factory=get_schema_parser_factory,
            # )
            # print(
            #     f"[DEBUG in process_response_from_reference] parse with empty body, response_config: {response_config}"
            # )
            # if self is ResponseStrategy.OBJECT:
            #     response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
            #     response_data_prop["name"] = response_schema_ref["title"]
            #     response_data_prop["required"] = _Default_Required.empty
            #     response_data_prop["type"] = "file"
            #     init_response["data"].append(response_data_prop)
            # else:
            #     self._ensure_data_structure_when_non_object_strategy(init_response)
            #     init_response["data"][response_schema_ref["title"]] = response_config

            # TODO: Study here how to implement
            # response_config = self._generate_response(
            #     init_response={},
            #     property_value={},  # It's {}
            #     get_schema_parser_factory=get_schema_parser_factory,
            #     property_key=empty_body_key,
            # )

            response_config = self._generate_empty_response()  # type: ignore[assignment]
            if "title" in response_schema_ref.keys() and response_schema_ref["title"] == "InputStream":
                if self is ResponseStrategy.OBJECT:
                    response_config["type"] = "file"
                else:
                    response_config = "random file output stream"  # type: ignore[assignment]

            if self is ResponseStrategy.OBJECT:
                response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
                print(f"[DEBUG in process_response_from_reference] response_data_prop: {response_data_prop}")
                response_data_prop["name"] = empty_body_key
                response_data_prop["required"] = empty_body_key in parser.get_required(default=[empty_body_key])
                init_response["data"].append(response_data_prop)
            else:
                self._ensure_data_structure_when_non_object_strategy(init_response)
                init_response["data"][empty_body_key] = response_config

            # empty_response = self._generate_empty_response()
            # if self is ResponseStrategy.OBJECT:
            #     response_data_prop = self._ensure_data_structure_when_object_strategy(
            #         init_response, empty_response
            #     )
            #     print(f"[DEBUG in process_response_from_reference] response_data_prop: {response_data_prop}")
            #     response_data_prop["name"] = empty_body_key
            #     response_data_prop["required"] = empty_body_key in parser.get_required(default=[empty_body_key])
            #     init_response["data"].append(response_data_prop)
            # else:
            #     self._ensure_data_structure_when_non_object_strategy(init_response)
            #     init_response["data"][empty_body_key] = empty_response
            # print(f"[DEBUG in process_response_from_reference] empty_response: {empty_response}")

            print(f"[DEBUG in process_response_from_reference] empty_body_key: {empty_body_key}")
            print(f"[DEBUG in process_response_from_reference] parse with empty body, init_response: {init_response}")
            return init_response
            # assert False
        # return init_response

    def process_response_from_data(
        self,
        init_response: dict,
        data: dict,
        get_schema_parser_factory: Callable,
    ) -> dict:
        response_config = self._generate_response(
            init_response=init_response,
            property_value=data,
            get_schema_parser_factory=get_schema_parser_factory,
        )
        if self is ResponseStrategy.OBJECT:
            response_data_prop = self._ensure_data_structure_when_object_strategy(init_response, response_config)
            init_response["data"].append(response_data_prop)
        else:
            self._ensure_data_structure_when_non_object_strategy(init_response)
            init_response["data"][0] = response_config
        return init_response

    def _ensure_data_structure_when_object_strategy(
        self, init_response: dict, response_data_prop: Union[str, dict, list]
    ) -> dict:
        assert isinstance(response_data_prop, dict)
        assert isinstance(
            init_response["data"], list
        ), "The response data type must be *list* if its HTTP response strategy is object."
        assert (
            len(list(filter(lambda d: not isinstance(d, dict), init_response["data"]))) == 0
        ), "Each column detail must be *dict* if its HTTP response strategy is object."
        return response_data_prop

    def _ensure_data_structure_when_non_object_strategy(self, init_response: dict) -> None:
        assert isinstance(
            init_response["data"], dict
        ), "The response data type must be *dict* if its HTTP response strategy is not object."

    def _generate_response(
        self,
        init_response: dict,
        property_value: dict,
        get_schema_parser_factory: Callable,
        property_key: str = "",
    ) -> Union[str, list, dict]:
        if not property_value:
            return self._generate_empty_response()
        print(f"[DEBUG in _generate_response] property_value: {property_value}")
        ref_schema = get_schema_parser_factory().reference_object().has_ref(property_value)
        if ref_schema:
            print(f"[DEBUG in _generate_response] before it have ref_schema: {ref_schema}")
            print(f"[DEBUG in _generate_response] before it have init_response: {init_response}")
            print(f"[DEBUG in _generate_response] before it have resp_2: {property_value}")
            # if ref_schema == "ref":
            #     resp = self.process_response_from_reference(
            #         init_response=init_response,
            #         data=property_value,
            #         get_schema_parser_factory=get_schema_parser_factory,
            #     )
            #     print(f"[DEBUG in _generate_response] resp: {resp}")
            #     return resp
            # else:
            # if ref_schema == "ref":
            #     resp_1 = self._generate_response_from_data(
            #         init_response=init_response,
            #         resp_prop_data=property_value,
            #         get_schema_parser_factory=get_schema_parser_factory,
            #     )
            # else:
            # # Currently solution
            resp_1 = self._generate_response_from_data(
                init_response=init_response,
                resp_prop_data=get_schema_parser_factory().reference_object().get_schema_ref(property_value),
                get_schema_parser_factory=get_schema_parser_factory,
            )
            # # test ...

            # resp_1 = self._process_reference_object(
            #     init_response=init_response,
            #     response_schema_ref=get_schema_parser_factory().reference_object().get_schema_ref(property_value),
            #     get_schema_parser_factory=get_schema_parser_factory,
            #     empty_body_key=property_key,
            # )
            print(f"[DEBUG in _generate_response] resp_1: {resp_1}")
            # resp_2 = self.process_response_from_reference(
            #     init_response=init_response,
            #     data=property_value,
            #     get_schema_parser_factory=get_schema_parser_factory,
            # )
            # print(f"[DEBUG in _generate_response] resp_2: {resp_2}")
            # Find the specific element and return it
            # for e in resp_2["data"]:
            #     print(f"[DEBUG in _generate_response] e: {e}")
            #     if e["name"] in property_value[f"${ref_schema}"]:
            #         assert isinstance(e, dict)
            #         print(f"[DEBUG in _generate_response] under resp_2 e: {e}")
            #         return e
            # Note:
            # Data format should be like:
            # {
            #      "name": "",
            #      "required": _Default_Required.empty,
            #      "type": None,
            #      "format": None,
            #      "items": [],
            # }
            return resp_1
            # assert False
        else:
            resp_from_data = self._generate_response_from_data(
                init_response=init_response,
                resp_prop_data=property_value,
                get_schema_parser_factory=get_schema_parser_factory,
            )
            print(f"[DEBUG in _generate_response] resp_from_data: {resp_from_data}")
            return resp_from_data

    def _generate_empty_response(self) -> Union[str, Dict[str, Any]]:
        if self is ResponseStrategy.OBJECT:
            return {
                "name": "",
                "required": _Default_Required.empty,
                "type": None,
                "format": None,
                "items": [],
            }
        else:
            return "empty value"

    def _generate_response_from_reference(self, ref_data: dict) -> Union[str, Dict[str, Any]]:
        if self is ResponseStrategy.OBJECT:
            return {
                "name": "",
                "required": _Default_Required.general,
                # TODO: Set the *type* property correctly
                "type": "file",
                # TODO: Set the *format* property correctly
                "format": None,
                "items": [],
                "FIXME": "Handle the reference",
            }
        else:
            return "FIXME: Handle the reference"

    def _generate_response_from_data(
        self,
        init_response: dict,
        resp_prop_data: dict,
        get_schema_parser_factory: Callable,
    ) -> Union[str, list, dict]:

        def _handle_list_type_data(
            data: dict, noref_val_process_callback: Callable, ref_val_process_callback: Callable, response: dict = {}
        ) -> dict:
            items_data = data["items"]
            if get_schema_parser_factory().reference_object().has_ref(items_data):
                response = _handle_reference_object(
                    response, items_data, noref_val_process_callback, ref_val_process_callback
                )
            else:
                print(f"[DEBUG in _handle_list_type_data] init_response: {init_response}")
                print(f"[DEBUG in _handle_list_type_data] items_data: {items_data}")
                response_value = self._generate_response_from_data(
                    init_response=init_response,
                    resp_prop_data=items_data,
                    get_schema_parser_factory=get_schema_parser_factory,
                )
                print(f"[DEBUG in _handle_list_type_data] response_value: {response_value}")
                if isinstance(response_value, list):
                    # TODO: Need to check whether here logic is valid or not
                    response = response_value  # type: ignore[assignment]
                elif isinstance(response_value, dict):
                    # TODO: Need to check whether here logic is valid or not
                    response = response_value
                else:
                    assert isinstance(response_value, str)
                    response = response_value  # type: ignore[assignment]
                print(f"[DEBUG in _handle_list_type_data] response: {response}")
            return response

        def _handle_reference_object(
            response: dict, items_data: dict, noref_val_process_callback: Callable, ref_val_process_callback: Callable
        ) -> dict:
            single_response = get_schema_parser_factory().reference_object().get_schema_ref(items_data)
            parser = get_schema_parser_factory().object(single_response)
            for item_k, item_v in parser.get_properties(default={}).items():
                print(f"[DEBUG in nested data issue at _handle_list_type_data] item_v: {item_v}")
                print(f"[DEBUG in nested data issue at _handle_list_type_data] response: {response}")
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] parser.get_required(): {parser.get_required()}"
                )
                if get_schema_parser_factory().reference_object().has_ref(item_v):
                    response = ref_val_process_callback(item_k, item_v, response, parser, noref_val_process_callback)
                else:
                    response = noref_val_process_callback(item_k, item_v, response)
            return response

        def _handle_list_type_value_with_object_strategy(data: dict) -> dict:

            def _ref_process_callback(
                item_k: str, item_v: dict, response: dict, parser, noref_val_process_callback: Callable
            ) -> dict:
                item_k_data_prop = {
                    "name": item_k,
                    "required": item_k in parser.get_required(),
                    "type": convert_js_type(item_v.get("type", "object")),
                    # TODO: Set the *format* property correctly
                    "format": None,
                    "items": [],
                }
                ref_item_v_response = _handle_reference_object(
                    items_data=item_v,
                    noref_val_process_callback=noref_val_process_callback,
                    ref_val_process_callback=_ref_process_callback,
                    response=item_k_data_prop,
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] ref_item_v_response from data which has reference object: {ref_item_v_response}"
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] response from data which has reference object: {response}"
                )
                print(f"[DEBUG in _handle_list_type_data] check whether the itme is empty or not: {response['items']}")
                if response["items"]:
                    print("[DEBUG in _handle_list_type_data] the response item has data")
                    response["items"].append(ref_item_v_response)
                else:
                    print("[DEBUG in _handle_list_type_data] the response item doesn't have data")
                    response["items"] = (
                        [ref_item_v_response] if not isinstance(ref_item_v_response, list) else ref_item_v_response
                    )
                return response

            def _noref_process_callback(item_k: str, item_v: dict, response_data_prop: dict) -> dict:
                item_type = convert_js_type(item_v["type"])
                item = {"name": item_k, "required": _Default_Required.general, "type": item_type}
                assert isinstance(
                    response_data_prop["items"], list
                ), "The data type of property *items* must be *list*."
                response_data_prop["items"].append(item)
                return response_data_prop

            response_data_prop = {
                "name": "",
                "required": _Default_Required.general,
                "type": v_type,
                # TODO: Set the *format* property correctly
                "format": None,
                "items": [],
            }
            response_data_prop = _handle_list_type_data(
                data=data,
                noref_val_process_callback=_noref_process_callback,
                ref_val_process_callback=_ref_process_callback,
                response=response_data_prop,
            )
            return response_data_prop

        def _handle_object_type_value_with_object_strategy(data: dict) -> dict:
            print(f"[DEBUG in _handle_object_type_value_with_object_strategy] data: {data}")
            data_title = data.get("title", "")
            if data_title:
                # TODO: It should also consider the scenario about input stream part (download file)
                # Example data: {'type': 'object', 'title': 'InputStream'}
                if re.search(data_title, "InputStream", re.IGNORECASE):
                    return {
                        "name": "",
                        "required": _Default_Required.general,
                        "type": "file",
                        # TODO: Set the *format* property correctly
                        "format": None,
                        "items": None,
                    }
                else:
                    raise NotImplementedError

            has_ref = get_schema_parser_factory().reference_object().has_ref(data)

            # if get_schema_parser_factory().reference_object().has_ref(data):
            #     resp = self.process_response_from_reference(
            #         init_response=init_response,
            #         data=data,
            #         get_schema_parser_factory=get_schema_parser_factory,
            #     )
            #     print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
            #     return resp["data"]
            # elif "additionalProperties" in data.keys():

            # Check reference first
            if has_ref:
                # Process reference
                resp = self.process_response_from_reference(
                    init_response=init_response,
                    data=data,
                    get_schema_parser_factory=get_schema_parser_factory,
                )
                print(f"[DEBUG in _handle_object_type_value_with_object_strategy] has reference schema")
                print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
                return resp["data"]
            else:
                # Process schema *additionalProperties* but without reference
                if "additionalProperties" in data.keys():
                    # Handle the schema *additionalProperties*
                    additional_properties = data["additionalProperties"]
                    additional_properties_type = convert_js_type(additional_properties["type"])
                    if locate(additional_properties_type) in [list, dict, "file"]:
                        items_config_data = _handle_list_type_value_with_object_strategy(additional_properties)
                        print(
                            f"[DEBUG in _handle_object_type_value_with_object_strategy] items_config_data: {items_config_data}"
                        )
                        return {
                            "name": "",
                            "required": _Default_Required.general,
                            "type": additional_properties_type,
                            # TODO: Set the *format* property correctly
                            "format": None,
                            "items": [items_config_data],
                        }
                    else:
                        return {
                            "name": "",
                            "required": _Default_Required.general,
                            "type": additional_properties_type,
                            # TODO: Set the *format* property correctly
                            "format": None,
                            "items": None,
                        }
                else:
                    # FIXME: it should focus on processing the config data which data structure is for one specific
                    #  column, not for entire object.
                    # Process non-reference
                    resp = self.process_response_from_reference(
                        init_response={"strategy": ResponseStrategy.OBJECT, "data": []},
                        data=data,
                        get_schema_parser_factory=get_schema_parser_factory,
                        parse_from_schema=False,
                    )
                    print(
                        f'[DEBUG in _handle_object_type_value_with_object_strategy] before *"additionalProperties" in data.keys()* data: {data}'
                    )
                    print(
                        f"[DEBUG in _handle_object_type_value_with_object_strategy] don't have reference schema, it's the self data content"
                    )
                    print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
                    assert False
                    # return {
                    #     "name": "",
                    #     "required": _Default_Required.general,
                    #     "type": "dict",
                    #     # TODO: Set the *format* property correctly
                    #     "format": None,
                    #     "items": resp["data"],
                    # }

                # if not get_schema_parser_factory().reference_object().has_ref(data):
                #     resp = self.process_response_from_reference(
                #         init_response={"strategy": ResponseStrategy.OBJECT, "data": []},
                #         data=data,
                #         get_schema_parser_factory=get_schema_parser_factory,
                #         parse_from_schema=False,
                #     )
                #     print(f"[DEBUG in _handle_object_type_value_with_object_strategy] don't have reference schema, it's the self data content")
                #     print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
                #     return {
                #         "name": "",
                #         "required": _Default_Required.general,
                #         "type": "dict",
                #         # TODO: Set the *format* property correctly
                #         "format": None,
                #         "items": resp["data"],
                #     }
                # resp = self.process_response_from_reference(
                #     init_response=init_response,
                #     data=data,
                #     get_schema_parser_factory=get_schema_parser_factory,
                # )
                # print(f"[DEBUG in _handle_object_type_value_with_object_strategy] has reference schema")
                # print(f"[DEBUG in _handle_object_type_value_with_object_strategy] resp: {resp}")
                # return resp["data"]
                # return {
                #     "name": "",
                #     "required": _Default_Required.general,
                #     "type": "FIXME",
                #     # TODO: Set the *format* property correctly
                #     "format": None,
                #     "items": None,
                # }
                # raise NotImplementedError(
                #     "It should re-consider the parsing logic about handle object type config with object strategy."
                # )

        def _handle_other_types_value_with_object_strategy(v_type: str) -> dict:
            return {
                "name": "",
                "required": _Default_Required.general,
                "type": v_type,
                # TODO: Set the *format* property correctly
                "format": None,
                "items": None,
            }

        def _handle_list_type_value_with_non_object_strategy(data: dict) -> list:

            def _ref_process_callback(
                item_k: str, item_v: dict, response: dict, parser, noref_val_process_callback: Callable
            ) -> dict:
                ref_item_v_response = _handle_reference_object(
                    items_data=item_v,
                    noref_val_process_callback=noref_val_process_callback,
                    ref_val_process_callback=_ref_process_callback,
                    response={},
                )
                response[item_k] = ref_item_v_response
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] ref_item_v_response from data which has reference object: {ref_item_v_response}"
                )
                print(
                    f"[DEBUG in nested data issue at _handle_list_type_data] response from data which has reference object: {response}"
                )
                return response

            def _noref_process_callback(item_k: str, item_v: dict, item: dict) -> dict:
                item_type = convert_js_type(item_v["type"])
                print(
                    f"[DEBUG in src] _handle_list_type_value_with_non_object_strategy._noref_process_callback item_type: {item_type}"
                )
                if locate(item_type) is str:
                    # lowercase_letters = string.ascii_lowercase
                    # random_value = "".join([random.choice(lowercase_letters) for _ in range(5)])
                    random_value = "random string value"
                elif locate(item_type) is int:
                    # random_value = int(
                    #     "".join([random.choice([f"{i}" for i in range(10)]) for _ in range(5)]))
                    random_value = "random integer value"
                elif locate(item_type) == bool:
                    random_value = "random boolean value"
                else:
                    raise NotImplementedError
                item[item_k] = random_value
                return item

            item_info: dict = {}
            item_info = _handle_list_type_data(
                data=data,
                noref_val_process_callback=_noref_process_callback,
                ref_val_process_callback=_ref_process_callback,
                response=item_info,
            )
            return [item_info]

        def _handle_each_data_types_response_with_object_strategy(data: dict, v_type: str) -> dict:
            if locate(v_type) == list:
                return _handle_list_type_value_with_object_strategy(data)
            elif locate(v_type) == dict:
                return _handle_object_type_value_with_object_strategy(data)
            else:
                return _handle_other_types_value_with_object_strategy(v_type)

        def _handle_each_data_types_response_with_non_object_strategy(
            resp_prop_data: dict, v_type: str
        ) -> Union[str, list, dict]:
            if locate(v_type) == list:
                return _handle_list_type_value_with_non_object_strategy(resp_prop_data)
            elif locate(v_type) == dict:
                data_title = resp_prop_data.get("title", "")
                if data_title:
                    # TODO: It should also consider the scenario about input stream part (download file)
                    # Example data: {'type': 'object', 'title': 'InputStream'}
                    if re.search(data_title, "InputStream", re.IGNORECASE):
                        return "random file output stream"
                    else:
                        raise NotImplementedError

                additional_properties = resp_prop_data["additionalProperties"]
                if get_schema_parser_factory().reference_object().has_ref(additional_properties):
                    return self.process_response_from_reference(
                        init_response=init_response,
                        data=additional_properties,
                        get_schema_parser_factory=get_schema_parser_factory,
                    )["data"]
                else:
                    return self.process_response_from_data(
                        init_response=init_response,
                        data=additional_properties,
                        get_schema_parser_factory=get_schema_parser_factory,
                    )["data"][0]
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
        if not resp_prop_data.get("type", None):
            assert get_schema_parser_factory().reference_object().has_ref(resp_prop_data)
            return _handle_each_data_types_response_with_object_strategy(resp_prop_data, "dict")
        v_type = convert_js_type(resp_prop_data["type"])
        if self is ResponseStrategy.OBJECT:
            return _handle_each_data_types_response_with_object_strategy(resp_prop_data, v_type)
        else:
            return _handle_each_data_types_response_with_non_object_strategy(resp_prop_data, v_type)


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
