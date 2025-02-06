# Value format

## ``format``

The value format setting.


### ``format.strategy``

The strategy how it should use to generate value with specific format way. It would set the value format as
`BY_DATA_TYPE` in default.

The following format strategies are provided by **_PyFake-API-Server_**:

| Strategy name   | Purpose                                                                                 |
|:----------------|:----------------------------------------------------------------------------------------|
| `BY_DATA_TYPE`  | Randomly generate value by the setting data type                                        |
| `FROM_ENUMS`    | Randomly generate value from an array                                                   |
| `CUSTOMIZE`     | Randomly generate value by customization value which may includes the [format variable] |
| `FROM_TEMPLATE` | Use the [format setting] in ``template`` section to randomly generate value             |

  [format variable]: ./format_variable.md
  [format setting]: ../../../template/common_config/format.md


### ``format.digit``

Set the digit setting of the value.

!!! info "Not for every value"

    This property would be great to use for numeric type value only. A
    non-numeric type value, i.e., pure string type or boolean type value,
    is not necessary and is not also ineffective with this property.

About more details, please refer to [here](#formatdigit_1).


### ``format.size``

Set the value size of the value.

!!! info "Size in different meanings for different types"

    A size of value could be 2 meanings:

    * For a numeric type value, it means maximum and minimum.
    * For a non-numeric type value like string type one, it means the
    length of value.

About more details, please refer to [here](#formatsize_1).


### ``format.enums``

If the value must be one of multiple values, it could set the multiple values as an array at this property. The value
would be randomly generated from the array.

Activate to use this property with strategy `FROM_ENUMS`.


### ``format.customize``

If the value format is complex, or it would be duplicate appeared in other multiple settings like response, it could 
reuse the value format setting at this property.

Activate to use this property with strategy `CUSTOMIZE`.

!!! tip "Usually be used with property ``format.variables`` or ``template.common_config.format``"

    About using property ``format.variables``, it must need to run with
    format setting variables. In **_PyFake-API-Server_** configuration, the
    format setting variables would only be set and get from 2 places:
    at property ``format.variables`` or in section ``template.common_config.format``.
    
    About the usage guide, please refer to this [example](#__tabbed_1_2).


### ``format.variables``

Set the parts of format settings as variables at this property. And the variables should be used in property
``format.customize``.

Activate to use this property with strategy `CUSTOMIZE`.

About the usage guide, please refer to this [example](#__tabbed_1_2). For the details setting, please refer to [here](./format_variable.md).


### ``format.use_name``

Extract the entire format settings into ``template.common_config.format`` and use this property to reuse them.

Activate to use this property with strategy `FROM_TEMPLATE`.

About the usage guide, please refer to this [example](#__tabbed_1_4).

!!! example "Use customize"

    Let's easily demonstrate how to use property ``format.customize``.

    For example, we want to set a column ``fee``.
    
    === "In general setting"
            
        Just randomly generate with the data type and won't configure
        anything:
    
        ```yaml
        format:
          strategy: by_data_type
        ```

        This configuring way without any control. It even may response a
        negative value in response. If the column has some attribute like
        it must be a positive number, this is not a good way to configure.
    
        - [ ] Configure ``format`` setting to limit the value
        - [ ] Extract to configure ``format.variables`` setting into section
            ``template.common_config.format.variables`` for reusing
        - [ ] Extract to configure entire ``format`` setting into section
            ``template.common_config.format.entities`` for reusing
    
    === "Setting with ``format``"
        
        Limit the value should be radomly generated with the specific format
        and the ID must be in range 0 to 1000:
        
        ```yaml hl_lines="3-9"
        format:
          strategy: customize
          customize: amt_val USD
          variables:
            - name: amt_val
              value_format: int
              size:
                max: 1000
                min: 0
        ```

        In this way, it controls the value must be `XXX USD`, for exmaple, it
        maybe `123 USD`. This configurating way be more safer and more flexible
        to configure for generating some specific format value.
    
        - [X] Configure ``format`` setting to limit the value
        - [ ] Extract to configure ``format.variables`` setting into section
            ``template.common_config.format.variables`` for reusing
        - [ ] Extract to configure entire ``format`` setting into section
            ``template.common_config.format.entities`` for reusing

    === "Setting with ``format.variables`` in ``template``"
        
        In some requirement, the API would response more columns which format
        would be same as the ``id`` column, you have 2 choice to do:

        * Set deplicate setting in different columns
        * Extract the setting into section ``template`` and reuse it

        For the first one, it's easy and won't demonstrate here. Let's demonstrate
        the second one: how to extract the format setting?

        Set the format setting in ``template.common_config.format.variables``
        configuration section:
    
        ```yaml hl_lines="5-11"
        template:
          activate: true
          common_config:
            activate: true
            format:
              variables:
                - name: amt_val
                  value_format: int
                  size:
                    max: 1000
                    min: 0
        ```
        
        And you could clear the format setting of each columns they need in the
        specific API configuration as following:
    
        ```yaml hl_lines="2-3"
        format:
          strategy: customize
          customize: amt_val USD
        ```
        
        - [X] Configure ``format`` setting to limit the value
        - [X] Extract to configure ``format.variables`` setting into section
            ``template.common_config.format.variables`` for reusing
        - [ ] Extract to configure entire ``format`` setting into section
            ``template.common_config.format.entities`` for reusing

    === "Setting with ``format.entities`` in ``template``"
        
        Sometimes, it has multiple columns in one APIs or multiple APIs are mostly
        same, it's the time to reuse entire format setting. 

        Set the entire format setting in ``template.common_config.format.entities``
        configuration section:
    
        ```yaml hl_lines="6-10"
        template:
          activate: true
          common_config:
            activate: true
            format:
              entities:
                - name: usd_fee_value
                  config:
                    strategy: customize
                    customize: amt_val USD
              variables:
                - name: amt_val
                  value_format: int
                  size:
                    max: 1000
                    min: 0
        ```
        
        And you could modify the format setting of each columns they need in the
        specific APIs configuration as following:
    
        ```yaml hl_lines="2-3"
        format:
          strategy: from_template
          use_name: usd_fee_value
        ```
        
        - [X] Configure ``format`` setting to limit the value
        - [X] Extract to configure ``format.variables`` setting into section
            ``template.common_config.format.variables`` for reusing
        - [X] Extract to configure entire ``format`` setting into section
            ``template.common_config.format.entities`` for reusing


## ``format.digit``

If the value is a numeric format value, you could configure this property to set the digit settings of the value.


### ``format.digit.integer``

How many digit it would have at integer part of the value.


### ``format.digit.decimal``

How many digit it would have at decimal part of the value.

??? example "Set the value digit"

    Configuration:

    ```yaml
    - format:
        digit:
          integer: 6
          decimal: 4
    ```

    Result:

    ![format setting]
    [format setting]: ../../../../../_images/configure-references/format_digit_setting.png


## ``format.size``

Set the size of the value. These size has 2 different meanings:

* If value is numeric format value, the size means the maximum value and minimum value.
* If value is string type value, the size means the maximum of value length and the minimum of value length.

And it has 2 different ways to set:

* Set the value size from a range
* Set the value size as a specific value

### ``format.size.max_value``

The maximum value.


### ``format.size.min_value``

The minimum value.


### ``format.size.only_equal``

If the value should be formatted as a specific size, not be randomly generated from a range, use this property to let it
must be a specific size value.
