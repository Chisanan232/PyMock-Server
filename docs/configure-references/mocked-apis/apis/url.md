# URL

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
