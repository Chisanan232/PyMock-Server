# Subcommand ``pull`` usage

If it has already had API documentation, e.g., OpenAPI format (aka Swagger API), provides the API details, you could use
``pull`` feature to fetch it as **_PyFake-API-Server_** format configuration and set up HTTP server for mocking API easily and 
quickly.

??? question "Why we need sub-command line ``pull``?"

    Let's consider one scenario, the system has already provide service for a while 
    and it has so many APIs which have already be used awhile. However, you want to 
    import this tool for Font-End site development, but it's too hard to configure 
    all existing APIs into **_PyFake-API-Server_** configuration. At this time, ``pull`` 
    feature could give you a hand to handle it easily and quickly.


```console
>>> fake rest-server pull <option>
```


## ``--source`` or ``-s`` <API document URL\>

Set the source that is the endpoint of OpenAPI document it would try to get the API documentation configuration and 
convert it as **_PyFake-API-Server_** format configuration.

It receives a string value about the host address or URL path.


## ``--source-file`` or ``-f`` <API document configuration file\>

Set the source file that is the specific file it would try to get the API documentation configuration and convert it 
as **_PyFake-API-Server_** format configuration.

It receives a string value about the configuration file path.


## ``--base-url`` <base API path\>

Set the base URL for deserialization of API documentation configuration.

It receives a string value about the base URL path.


## ``--config-path`` or ``-c`` <config file path\>

The file path for saving configuration which be fetched and be deserialized from the API documentation configuration to 
**_PyFake-API-Server_** format.

It receives a string value about the configuration file path.


## ``--request-with-https``

If it's ``True``, it would find the Swagger API documentation host through ``HTTPS``, or it does through ``HTTP``
directly.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--base-file-path`` <directory path\>

The path which would be used as root path to find the other files.

It receives a string value about the base path.


## ``--include-template-config``

If it's ``True``, it would set the template settings in the output configuration.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--dry-run``

If it's ``True``, it would run the ``pull`` feature without result.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.


## ``--divide-api``

If it's ``True``, it would divide the configuration about mocked API part to another single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="8-51"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
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
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```


## ``--divide-http``

If it's ``True``, it would divide the configuration about the HTTP part of each mocked APIs to another single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="10-51"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
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
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```


## ``--divide-http-request``

If it's ``True``, it would divide the configuration about the request part in HTTP section of each mocked APIs to another
single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="11-22"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
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
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```


## ``--divide-http-response``

If it's ``True``, it would divide the configuration about the response part in HTTP section of each mocked APIs to another
single file.

It doesn't accept any value and default is ``False``. It's ``True`` if set this option.

Let's demonstrate an example configuration for you. Below is a general entire configuration. If you set this option, it
would divide the highlight part and save it to another single file.

```yaml hl_lines="24-50"
name: ''
description: ''
mocked_apis:
  base:
    url: '/api/v1/test'
  apis:
    get_foo:
      url: '/foo'
      http:
        request:
          method: 'GET'
          parameters:
            - name: 'date'
              required: true
              default:
              type: str
              format:
            - name: 'fooType'
              required: true
              default:
              type: str
              format:
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
                - name: value2
                  required: True
                  type: str
      tag: 'foo'
```
