# Configure your APIs

It configures the detail settings of **_PyMock-API_** by YAML syntax, and must have either a ``.yml`` or ``.yaml`` file
extension. If you're new to YAML and want to learn more, see "[Learn YAML in Y minutes.]"

[Learn YAML in Y minutes.]: https://learnxinyminutes.com/docs/yaml/


## What settings are necessary?

content ...


## Set up API

content ...

```yaml
mocked_apis:
  <API name>: <API settings>
```

content ...

```yaml hl_lines="2"
mocked_apis:
  foo_home: <foo API settings>
```

content ...

### URL

content ...

```yaml hl_lines="3"
mocked_apis:
  foo_home:
    url: '/foo'
```

content ...

### HTTP

content ...

```yaml hl_lines="4"
mocked_apis:
  foo_home:
    url: '/foo'
    http: <HTTP settings>
```

content ...

#### Request

content ...

```yaml hl_lines="5-6"
mocked_apis:
  foo_home:
    url: '/foo'
    http:
      request:
        method: 'GET'
```

content ...

#### Response

content ...

```yaml hl_lines="7-8"
mocked_apis:
  foo_home:
    url: '/foo'
    http:
      request:
        method: 'GET'
      response:
        value: 'This is Foo home API.'
```

content ...


## Check configuration validation

content ...

```console
mock-api check -p <configuration path>
```

content ...
