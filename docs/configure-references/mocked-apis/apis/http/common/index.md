# Common schemas

Some property which would be commonly used.


### ``items``

This property is responsible for details setting of element in some data structure which is collection, e.g., list type 
or map (aka dictionary in Python realm) type data.

[Here](/configure-references/mocked-apis/apis/http/common/item_element) is the configuration details.


### ``format``

This property targets setting the value as specific format what you what to accept in request or return in response.

[Here](./value_format) is the configuration details.


#### ``format.variables``

About setting complex format, you must need to use property ``format.variables`` to help you configure. No matter for
reusable or readable setting for maintain, it could be stronger to help you configure complex format easily.

[Here](./format_variable.md) is the configuration details.
