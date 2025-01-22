# Common config - Format

## ``template.common_config.format``

The common settings about [value format] function for reusing in entire configration.

!!! tip "Only for specific format strategies"

    About reusing the settings, it only be activated by format strategy `CUSTOMIZE` and `FROM_TEMPLATE`.


### ``entities``

This property targets for reusing the entire setting of property ``format``.

Only be activated for format strategy ``FROM_TEMPLATE``.


#### ``entities[*].name``

The naming of the format setting. For outside setting, it would use the value of this property to identify which format
setting it should use to generate the random value. So in a format setting array ``entities``, this value must be unique.


#### ``entities[*].config``

The property ``format`` setting and it's totally same as [value format].

[value format]: ../../apis/http/common/value_format.md

!!! question "How to reuse entire format setting from ``format.entities``?"

    At the column which may be in [request] or [response], please use format
    strategy `FROM_TEMPLATE` and set the property ``format.use_name``:

    ```yaml
    format:
      strategy: from_template
      use_name: usd_fee_value
    ```

    And remember, don't forget the property ``format.use_name`` value must be
    exist in ``entities[*].name``.


### ``variables``

This property targets for reusing the setting of property ``format.variables``.

This is an array type property and the data type of element is totally same as [format variable].

Only be activated for format strategy ``CUSTOMIZE``.

[format variable]: ../../apis/http/common/format_variable.md

!!! question "How to reuse format variable setting from ``format.variables``?"

    At the column which may be in [request] or [response], please use format
    strategy `CUSTOMIZE` and set the property ``format.customize``:

    ```yaml
    format:
      strategy: customize
      customize: amt_val USD
    ```

[request]: ../../apis/http/request.md#parametersformat
[response]:../../apis/http/response.md#propertiesformat
