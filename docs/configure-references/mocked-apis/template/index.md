# Template

This configuration section could let your configuration be more clear and organized to read and manage.

For configuration, it let you could divide the configuration to be more readable. Even though only one file need to
maintain, it may have very heavy content in file. When you face the problem, that's the time to use organizing feature
of **_PyFake-API-Server_**.

=== "Before organizing"

    ``` { .sh .no-copy }
    .
    └─ api.yaml                       # A heavy config which includes multiple APIs setting
    ```

=== "After organizing"
    
    ``` { .sh .no-copy }
    .
    ├─ tag_foo/                       # A directory for `/foo` APIs which have tag `foo`
    │  ├─ get_foo_api.yaml            #   API GET `/foo`
    │  ├─ post_foo_api.yaml           #   API POST `/foo`
    │  ├─ put_foo_api.yaml            #   API PUT `/foo`
    │  └─ delete_foo_api.yaml/        #   API DELETE `/foo`
    ├─ tag_boo/                       # A directory for `/boo` APIs which have tag `boo`
    │  ├─ get_boo_api.yaml            #   API GET `/boo`
    │  └─ post_boo_api.yaml/          #   API POST `/boo`
    │                                 # For the APIs which doesn't have tag
    ├─ no_tag_get_wow_api/            #   API GET `/wow`
    ├─ no_tag_post_wow_api/           #   API POST `/wow`
    └─ api.yaml                       # The main configuration which as the entry point
    ```

For settings in configuration, it could let you set detail settings as variables for configuring or reuse the common
settings.

Here are some demonstration about randomly generate value with different configuring way

=== "Without control"
        
    Format setting in the specific API configuration:

    ```yaml
    format:
      strategy: by_data_type
    ```

=== "Control by ``format``"
    
    Format setting in the specific API configuration:
    
    ```yaml
    format:
      strategy: customize
      customize: var_num
      variables:
        - name: var_num
          value_format: int
          size:
            max: 100
            min: -200
    ```

=== "Reusing from ``template``"
    
    Format setting in ``template`` section configuration:

    ```yaml
    template:
      activate: true
      common_config:
        activate: true
        format:
          variables:
            - name: var_num
              value_format: int
              size:
                max: 100
                min: -200
    ```
    
    Format setting in the specific API configuration:

    ```yaml
    format:
      strategy: customize
      customize: var_num
    ```

## ``mocked_apis.template``

The setting section for the template feature.


### ``activate``

Whether activating the template feature or not. It accepts a boolean type value.


### ``file``

It's a setting section for some detail adjustments about loading configuration.

Please refer to [here](./file/index.md) to get more details.


### ``common_config``

Reusing common settings in **_PyFake-API-Server_** configuration.[^1]

  [^1]:
    Currently, it only supports reusing feature at property [format], but it
    is possible that supports being reusable in setting for more and more 
    properties in the future.

    [format]: ../apis/http/common/value_format.md

Please refer to [here](./common_config/index.md) to get more details.
