# Subcommand ``add`` usage

Doing something operations about configuration or its content.

```console
>>> mock-api add <option>
```


## ``--print-sample`` or ``-p``

Show the sample configuration which could be used directly by **_PyMock-API_**.

It doesn't accept any value.


## ``--generate-sample`` or ``-g``

Generating the sample configuration as a ``.yaml`` file. The configuration content is same as the output of running result
with option ``--print-sample``.

It doesn't accept any value.


## ``--output`` or ``-o`` <output-file-path\>

Generating the sample configuration to the target output file path.

It receives a value about the configuration file path, and it doesn't have default value. It would exit the program and
output error message if it doesn't have value of this option when using option ``--generate-sample``.


## ``--api-config-path`` <API configuration file path\>

Set the configuration file path to let this subcommand to operate with it.

It receives a value which is the configuration file path and default value is ``api.yaml``. It would face some scenarios:

* File exists

    No matter it has valid content or not, it would add the new API into the existed configuration.

* File doesn't exist

    It would generate a new configuration file add the new API to it.


## ``--api-path`` <URL\>

Set the URL path of mocking API.

It receives a string value and this is required option.

=== "Set by command line"
    
    ```console
    --api-path '/foo-home'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="2"
    mocked_apis:
      foo_home:
        # some settings of API
    ```


## ``--http-method`` <HTTP method\>

Set the HTTP method in request of mocking API.

It receives a string value which should satisfy the value of HTTP method which be defined in [RFC-2616](https://datatracker.ietf.org/doc/html/rfc2616#section-5.1.1).

=== "Set by command line"
    
    ```console
    --http-method 'POST'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="3-4"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
    ```


## ``--parameters`` <JSON format string value\>

Set the HTTP request parameters of mocking API.

It receives a string value and default value is empty string. This option could be used multiple times.

=== "Set by command line"
    
    ```console
    --parameters '{"name": "arg1", "required": true, "type": "str"}' --parameters '{"name": "arg2", "required": false, "type": "int", "default": 0}'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="5-12"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
          parameters:
            - name: 'arg1'
              required: true
              type: str
            - name: 'arg2'
              required: false
              type: int
              default: 0
    ```


## ``--response`` <String value\>

Set the HTTP response value of mocking API.

It receives a string value and default value is ``OK.``.

=== "Set by command line"
    
    ```console
    --response 'This is PyTest demo.'
    ```

=== "Set by YAML syntax"
    
    ```yaml hl_lines="13-14"
    mocked_apis:
      foo_home:
        request:
          method: 'POST'
          parameters:
            - name: 'arg1'
              required: true
              type: str
            - name: 'arg2'
              required: false
              type: int
              default: 0
        response:
          value: 'This is PyTest demo.'
    ```
