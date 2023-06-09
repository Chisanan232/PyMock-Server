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


## ``mocked_apis.<API name>.http.response``

This section is responsible for all settings of HTTP response.


## ``mocked_apis.<API name>.http.response.value``

The API response value. It would detect whether the value has extension or not. If it has, it would try to access the file
by the path to get the content as response value. If it hasn't, it would try to parse data as JSON format, and it would
respond string type value if it parses fail.
