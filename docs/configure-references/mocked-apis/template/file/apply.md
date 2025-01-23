# Template apply setting

## ``mocked_apis.template.apply``

The section about detail settings of applying which mocked APIs into entire **_PyMock-Server_** configuration.


### ``api``

It accepts 2 kinds of data: just a list or a list of dict type element.

* Just a list (Doesn't have tag)

    If it's just a list, the elements would are the file naming of all mocked API configurations which would be loaded
    into entire configuration.
    
    ```yaml
    apply:
      api:
        - get_foo
        - get_foo-boo
    ```

* A list of dict type element (Have tag for grouping mocked APIs)

    If it's just a list of dict type element, the key is the tag of mocked APIs like group name and the value is the
    list of elements which are the file naming of all mocked API configurations for loading into entire configuration.
    
    ```yaml
    apply:
      api:
        - foo:    # This is the mocked API *get_foo*'s tag
          - get_foo
        - foo-boo:    # This is the tag for mocked APIs *get_foo-boo* and *put_foo-boo*
          - get_foo-boo
          - put_foo-boo
    ```

!!! note "Only load the configuration it has in apply"

    If your loading setting only set ``apply``, it would ONLY load the mocked
    APIs which be set at the key ``api`` even it has other mocked APIs.
