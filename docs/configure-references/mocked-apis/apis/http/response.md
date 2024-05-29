# Response

``mocked_apis.<API name>.http.response``

This section is responsible for all settings of HTTP response.


## ``strategy``

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

### ``value``

The API response value it would use to return directly. It would try to parse data as JSON format, and it would respond 
string type value if it parses fail.


## File strategy

### ``path``

A file path which content is the API response value. It would detect the file extension and check whether it's valid or not. 
If it is, it would try to access the file by the path to get the content as response value. If it isn't, it would raise an 
exception **FileFormatNotSupport**.

Currently, it only supports _JSON_ file.


## Object strategy

### ``properties``

Express the response value as object of software realm. It accepts list type settings which would be combined as JSON format 
value to return.


#### ``properties[*].name``

The naming of value.


#### ``properties[*].required``

Whether value is required to response or not.


#### ``properties[*].type``

The data type of value. Please use Pythonic way to set this option.


#### ``properties[*].format``

The data format.


#### ``properties[*].items``

If the data type of value is list type, it should use this key to configure its element details. The element detail follow 
[item element settings](/configure-references/mocked-apis/apis/http/common/item_element).


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
