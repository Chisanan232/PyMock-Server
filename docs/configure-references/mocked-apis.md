# Mocked API settings

This configuration section is the major function because here settings would decide how your mocked API works.

## ``mocked_apis``

Manage the API detail settings. The elements in it would be key-value map format. The key means the common feature or API
name. The value means the detail settings of the common feature or API name.

So what is the common feature? **_PyMock-API_** provides some feature to let developers could to more convenience and clear
of configuring mocked API. Following are the common features it provides currently:

* [Basic information](#mocked_apisbase)


## ``mocked_apis.base``

The basic information of all APIs. It would apply this section settings for all APIs.


## ``mocked_apis.base.url``

The URL basic information of all APIs. It would apply the URL path to all API path. Let's give you an example to demonstrate:

```yaml
mocked_apis:
  base:
    url: '/test/v1'
```

Base on above settings to configure your mocked API, you would need to add the URL path ``/test/v1`` in font of the URL
path of all APIs. So your HTTP request URL would be like as below:

```console
http://127.0.0.1:9672/test/v1<API path>
```

And it's an empty string if you omit this setting. In the other words, you could use the API URL path you set directly.


## ``mocked_apis.<API name>``

The API you target to mock. The API name must be unique.


## ``mocked_apis.<API name>.url``

The URL path of API. Bellow are demonstrations the difference between only API and API with basic information settings:

=== "API URL Only"
    
    Only mocked API setting:
    
    ```yaml
    mocked_apis:
      foo_home:
        url: '/foo-home'
    ```

    It's API URL path would be the path you set.
    
    ```console
    http://127.0.0.1:9672/foo-home
    ```

=== "API URL with ``base`` settings"
    
    Mocked API setting with basic information setting:
    
    ```yaml hl_lines="2-3"
    mocked_apis:
      base:
        url: '/test/v1'
      foo_home:
        url: '/foo-home'
    ```
    
    It's API URL path would need to add basic URL path in font of it.

    ```console
    http://127.0.0.1:9672/test/v1/foo-home
    ```


## ``mocked_apis.<API name>.http``

The detail settings about HTTP. It has 2 major sections need to configure: [request](#mocked_apisapi-namehttprequest) and
[response](#mocked_apisapi-namehttpresponse).


## ``mocked_apis.<API name>.http.request``

This section is responsible for all settings of HTTP request.


## ``mocked_apis.<API name>.http.request.method``

The HTTP method which be accepted by API.


## ``mocked_apis.<API name>.http.request.parameters``

The parameter settings of API.


## ``mocked_apis.<API name>.http.request.parameters[*].name``

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


## ``mocked_apis.<API name>.http.request.parameters[*].required``

This is a boolean type value. If it's ``true``, web server would respond 400 error if the request misses the argument. Nor
it would ignore it.


## ``mocked_apis.<API name>.http.request.parameters[*].default``

The default value of parameter. If the parameter in request is empty or ``None`` value, it would use this value to process.


## ``mocked_apis.<API name>.http.request.parameters[*].type``

The data type of the parameter value API should accept. The setting value should be a valid type for Python realm, i.e.,
string type value as ``str``, integer type value as ``int``, etc. 

!!! note "What data type you should use?"

    As the description mention, the data type should be vallid for Python realm. Here provides some data type to help you
    configure your API parameters.
    
    * Text type value: ```str```
    * Integer type value: ```int```
    * Floating point number type value: ```float```
    * Boolean type value: ```bool```
    * Some object of list type value: ```list```
    * Key-value map type value: ```dict```


## ``mocked_apis.<API name>.http.request.parameters[*].format``

A regular expression of parameter value API should accept. It would respond 400 error if the parameter value format is not
satisfied.


## ``mocked_apis.<API name>.http.request.parameters[*].items``

If the data type of parameter value is list type, it should use this key to configure its element details. The element detail 
follow [item element settings](#items-element-settings).


## ``items element settings``

All the element of list type value follows these attributes to configure.


### ``items[*].name``

The naming of item's value.


### ``items[*].required``

Whether item's value is required to response or not.


### ``items[*].type``

The data type of item's value. Please use Pythonic way to set this option.


## ``mocked_apis.<API name>.http.response``

This section is responsible for all settings of HTTP response.


## ``mocked_apis.<API name>.http.response.strategy``

About the HTTP response data format, it has 3 different strategies provide developers to set and use in their development.

  * ``string``

    Return HTTP response as any format, any content which is string type value.

    Please refer to [here](#string-strategy) to get more detail settings of this strategy.

  * ``file``

    The HTTP response content would be imported from one specific file as string type value.

    Please refer to [here](#file-strategy) to get more detail settings of this strategy.

  * ``object``

    Express the HTTP response through object like software development. It's deeply recommended use this way to configure 
    HTTP response to be more clear and maintainable.

    Please refer to [here](#object-strategy) to get more detail settings of this strategy.


## String strategy

### ``mocked_apis.<API name>.http.response.value``

The API response value it would use to return directly. It would try to parse data as JSON format, and it would respond 
string type value if it parses fail.


## File strategy

### ``mocked_apis.<API name>.http.response.path``

A file path which content is the API response value. It would detect the file extension and check whether it's valid or not. 
If it is, it would try to access the file by the path to get the content as response value. If it isn't, it would raise an 
exception **FileFormatNotSupport**.

Currently, it only supports _JSON_ file.


## Object strategy

### ``mocked_apis.<API name>.http.response.properties``

Express the response value as object of software realm. It accepts list type settings which would be combined as JSON format 
value to return.


### ``mocked_apis.<API name>.http.response.properties[*].name``

The naming of value.


### ``mocked_apis.<API name>.http.response.properties[*].required``

Whether value is required to response or not.


### ``mocked_apis.<API name>.http.response.properties[*].type``

The data type of value. Please use Pythonic way to set this option.


### ``mocked_apis.<API name>.http.response.properties[*].format``

The data format.


### ``mocked_apis.<API name>.http.response.properties[*].items``

If the data type of value is list type, it should use this key to configure its element details. The element detail follow 
[item element settings](#items-element-settings).


Let's demonstrate the same HTTP response with each different strategies.

For focussing on the HTTP response difference configuring with each strategy, it fixes all settings which is not relative 
with response. And let's use value ``{"errorMessage": "", "responseCode": "200", "responseData": [{"id": 1, "name": "first ID", "value1": "demo value"}]}`` 
to demonstrate.

=== "HTTP response with **string** strategy"

    Set the value as string directly. If the value is more bigger, the configuration would be more harder to read and maintain.
    However, this is the easiest and quickest way to configure.
    
    The API configuration:

    ```yaml hl_lines="7-9"
    mocked_apis:
      foo_home:
        url: '/foo-strategy-demo'
        http:
          request:
            method: 'GET'
          response:
            strategy: string
            value: '{"errorMessage": "", "responseCode": "200", "responseData": [{"id": 1, "name": "first ID", "value1": "demo value"}]}'
    ```

=== "HTTP response with **file** strategy"

    The the value is too big to let developers read and maintain the configuration. It also could divide the value as content 
    in a single file to manage it. It could let the configuration to be more simpler. But it also would be a little bit annoying
    because you should read the setting between multiple different files.
    
    The API configuration:

    ```yaml hl_lines="7-9"
    mocked_apis:
      foo_home:
        url: '/foo-strategy-demo'
        http:
          request:
            method: 'GET'
          response:
            strategy: file
            path: ./demo-response-from-file.json
    ```
    
    The JSON file ``./demo-response-from-file.json`` which saves the HTTP response:

    ```json
    {
      "errorMessage": "", 
      "responseCode": "200", 
      "responseData": [
        {
          "id": 1, 
          "name": "first ID", 
          "value1": "demo value"
        }
      ]
    }
    ```

=== "HTTP response with **object** strategy"

    Set the response value as object of software developmenet. This way is the most flexible to maintain for developers 
    because it could set the details by each property of response value. But it also would let the settings to be more 
    longer in configuration. So it's obvious the configuration with this way is more complexer.
    
    The API configuration:

    ```yaml hl_lines="7-31"
    mocked_apis:
      foo_home:
        url: '/foo-strategy-demo'
        http:
          request:
            method: 'GET'
          response:
            strategy: object
            properties:
              - name: errorMessage
                required: True
                type: str
                format:
              - name: responseCode
                required: True
                type: str
                format:
              - name: responseData
                required: False
                type: list
                format:
                items:
                  - name: id
                    required: True
                    type: int
                  - name: name
                    required: True
                    type: str
                  - name: value1
                    required: True
                    type: str
    ```
