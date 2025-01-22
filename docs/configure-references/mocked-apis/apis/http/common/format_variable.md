# Variablilize value format

## ``format.variables``: value format settings as variables

Setting the value format with some specific settings which be configured as variables.


### ``format.variables[*].name``

The naming of the format setting. For outside setting, it would use the value of this property to identify which format
setting it should use to generate the random value. So in a format variable array, this value must be unique.


### ``format.variables[*].value_format``

The format type how it should generate the random value.

The following format types are provided by **_PyMock-Server_**:

| Strategy name | Purpose                                                     | Example result                       |
|:--------------|:------------------------------------------------------------|--------------------------------------|
| `str`         | Randomly generate value as string type value                | hjwgowjf                             |
| `int`         | Randomly generate value as integer type value               | 123456                               |
| `big_decimal` | Randomly generate value as decimal type value               | 123456678.123456                     |
| `bool`        | Randomly generate value as boolean type value               | true                                 |
| `date`        | Randomly generate string type value as date format          | 2025-01-22                           |
| `date-time`   | Randomly generate string type value as date and time format | 2025-01-25T16:19:08                  |
| `enum`        | Randomly generate value from an array                       | val1 in [val1, val2, val3]           |
| `email`       | Randomly generate string type value as email format[^1]     | twfsdg@gmail                         |
| `uuid`        | Randomly generate string type value as UUID format          | d2ecff78-d899-11ef-891f-be31ef195676 |
| `uri`         | Randomly generate string type value as URI[^2] format       | https://www.fkjgsj.com               |
| `url`         | Randomly generate string type value as [URL] format         | https://www.fkjgsj.com               |
| `ipv4`        | Randomly generate string type value as [IPv4] format        | 172.30.15.101                        |
| `ipv6`        | Randomly generate string type value as [IPv6] format        | 2001:db8:2de::e13                    |

[^1]:
  Currently, it only supports randomly generate email as ``gmail``, ``outlook``
  or ``yahoo``.

[^2]:
  About the URI (uniform resource identifiers) specification, it haa been
  defined twice in RFC: [RFC 2396] and [RFC 3986].

[RFC 2396]: https://datatracker.ietf.org/doc/html/rfc2396
[RFC 3986]: https://datatracker.ietf.org/doc/html/rfc3986
[URL]: https://datatracker.ietf.org/doc/html/rfc1738
[IPv4]: https://datatracker.ietf.org/doc/html/rfc791
[IPv6]: https://datatracker.ietf.org/doc/html/rfc2460

### ``format.variables[*].digit``

Set the digit setting of the value.

This property is the totally same function with [format.digit].

[format.digit]: ./value_format.md#formatdigit_1


### ``format.variables[*].size``

Set the value size of the value.

This property is the totally same function with [format.size].

[format.size]: ./value_format.md#formatsize_1


### ``format.variables[*].enum``

If the value must be one of multiple values, it could set the multiple values as an array at this property. The value
would be randomly generated from the array.

This property is the totally same function with [format.enums].

[format.enums]: ./value_format.md#formatenums
