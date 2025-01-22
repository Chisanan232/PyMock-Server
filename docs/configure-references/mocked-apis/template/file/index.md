# Template about configuration file

This configuration section could let your configuration be more clear and organized to read and manage. It let you could
separate each major sections, e.g., a mocked API or a HTTP section of one mocked API, to a single file so that one configuration
could be short and simple for reading easily.


## ``mocked_apis.template.file``

The setting section for the template feature.


### ``activate``

Whether activating the template feature or not. It accepts a boolean type value.


### ``load_config``

It's a setting section for some detail adjustments about loading configuration. Please refer to 
[here](./load.md) to get more details.


### ``config_path_values``

It's a setting section for some detail setting for scanning file to load configuration. Please refer to 
[here](./config_path_values.md) to get more details.


### ``apply``

It's a setting section for some detail setting for applying some specific mocked APIs into entire configuration. Please
refer to [here](./apply.md) to get more details.
