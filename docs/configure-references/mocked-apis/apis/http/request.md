# Request

## ``mocked_apis.<API name>.http.request``

This section is responsible for all settings of HTTP request.


### ``method``

The HTTP method which be accepted by API.


### ``parameters``

The parameter settings of API.


#### ``parameters[*].name``

The name of parameter.

Example of usage:

=== "HTTP method is GET"
    
    ```yaml hl_lines="7-8"
    mocked_apis:
      foo_home:
        url: '/foo-home'
        http:
          request:
            method: 'GET'
            parameters:
              - name: 'arg1'
    ```

=== "HTTP method is POST"
    
    ```yaml hl_lines="7-8"
    mocked_apis:
      foo_home:
        url: '/foo-home'
        http:
          request:
            method: 'POST'
            parameters:
              - name: 'arg1'
    ```

Then you could use the parameter ``arg1`` of API ``/foo-home``.

=== "Send HTTP request by GET method"
    
    ```console
    curl -X GET http://127.0.0.1:9672/foo-home?arg1=value
    ```

=== "Send HTTP request by POST method"
    
    ```console
    curl -X POST http://127.0.0.1:9672/foo-home -H 'Content-Type: application/json' -d '{"arg1":"value"}'
    ```


#### ``parameters[*].required``

This is a boolean type value. If it's ``true``, web server would respond 400 error if the request misses the argument. Nor
it would ignore it.

!!! tip "If insisting on requesting without required parameter ..."

    If you set a request parameter as required and you insisting
    on requesting without it, server would reutnr a 400 response
    with invalid message:

    ![miss required param](../../../../_images/configure-references/requesting_when_missing_param.png)


#### ``parameters[*].default``

The default value of parameter. If the parameter in request is empty or ``None`` value, it would use this value to process.


#### ``parameters[*].type``

The data type of the parameter value API should accept. The setting value should be a valid type for Python realm, i.e.,
string type value as ``str``, integer type value as ``int``, etc. 

Please refer to [Python built-in types](https://docs.python.org/3/library/stdtypes.html) document to get more detail if
you need.

!!! note "What data type you should use?"

    As the description mention, the data type should be vallid
    for Python realm. Here provides some data type to help you
    configure your API parameters.
    
    | Data type | Purpose                        |
    |:----------|:-------------------------------|
    | `str`     | Text type value                |
    | `int`     | Integer type value             |
    | `bool`    | Boolean type value             |
    | `list`    | Some object of list type value |
    | `dict`    | Key-value map type value       |

!!! tip "If insisting on requesting with invalid type parameter ..."

    If you set a request parameter as one specific data type and
    you insisting on requesting with invalid type of it, server
    would reutnr a 4XX response with invalid message:

    === "Response in Flask"

        In Flask server, it would response a 400 error.
    
        ![miss required param](../../../../_images/configure-references/requesting_when_invalid_type_param_in_flask.png)
    
    === "Response in FastAPI"

        In FastAPI server, it would got failure at the property of
        request parameter data model and response a 422 error.
    
        ![miss required param](../../../../_images/configure-references/requesting_when_invalid_type_param_in_fastapi.png)


#### ``parameters[*].format``

A regular expression of parameter value API should accept. It would respond 400 error if the parameter value format is not
satisfied.

About the setting details, please refer to [here](./common/value_format.md).

!!! tip "If insisting on requesting as invalid format value at the parameter ..."

    If you set a request parameter as one specific value format
    and you insisting on requesting with invalid format of its
    value, server would reutnr a 4XX response with invalid message.

    Let's demonstrate the invalid format value in request parameter
    with format strategy `FROM_ENUMS`:

    === "Response in Flask"

        In Flask server, it would response a 400 error.
    
        ![miss required param](../../../../_images/configure-references/requesting_when_invalid_format_param_in_flask.png)
    
    === "Response in FastAPI"

        In FastAPI server, it would got failure at the property of
        request parameter data model and response a 400 error.
    
        ![miss required param](../../../../_images/configure-references/requesting_when_invalid_format_param_in_fastapi.png)


#### ``parameters[*].items``

If the data type of parameter value is list type, it should use this key to configure its element details. The element detail 
follow [item element settings](/configure-references/mocked-apis/apis/http/common/item_element).
