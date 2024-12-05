# Configure your APIs

It configures the detail settings of **_PyMock-Server_** by YAML syntax, and must have either a ``.yml`` or ``.yaml`` file
extension. If you're new to YAML and want to learn more, see "[Learn YAML in Y minutes.]"

[Learn YAML in Y minutes.]: https://learnxinyminutes.com/docs/yaml/


## What settings are necessary?

This question also means what an API need? In generally, the necessary conditions it needs as following:

* [The URL path](#url)
* [The HTTP attributes](#http)
    * [HTTP request](#request)
    * [HTTP response](#response)

Therefore, above properties also are the options we must configure by YAML syntax for mocking API.


## Configure API

First of all, create a file with YAML extension ``.yaml``.

All the API settings need to be configured under key ``mocked_apis`` and it would be a list of key-value map type elements.
The key is the API name and the value is the detail settings of the API.

```yaml
mocked_apis:
  <API name>: <API settings>
```

Before start to configure, let's give a usage scenario: 

> Mock an API which accepts GET method without any parameter, and it would return string value ``This is Foo home API.``.
> We could sort out the requirement as 3 conditions as below:
> 
> * URL path: /foo
> * HTTP request method: GET
> * HTTP response data: This is Foo home API.

Let's name the API as ``foo_home``:

```yaml hl_lines="2"
mocked_apis:
  foo_home: <foo API settings>
```

### URL

In the API setting section, it uses key ``url`` to configure the URL path. So we could set ``/foo`` directly here:

```yaml hl_lines="3"
mocked_apis:
  foo_home:
    url: '/foo'
```

We have done the first condition! Let's quickly set the next one setting about HTTP.

> - [X] URL path: /foo
> - [ ] HTTP request method: GET
> - [ ] HTTP response data: This is Foo home API.

### HTTP

About the HTTP settings, it has multiple options could configure. So key ``http`` manages all settings about HTTP settings
and more details under it.

```yaml hl_lines="4"
mocked_apis:
  foo_home:
    url: '/foo'
    http: <HTTP settings>
```

In basically, there are 2 options we must configure: **HTTP request** and **HTTP response**. It also has 2 keys ``request``
and ``response`` to manage them.

#### Request

All the HTTP request settings would be managed under key ``http.request``. And right now, we just need to set one attribute
``method`` about the HTTP method:

```yaml hl_lines="5-6"
mocked_apis:
  foo_home:
    url: '/foo'
    http:
      request:
        method: 'GET'
```

We have done the second condition! It leaves only one condition about HTTP response.

> - [X] URL path: /foo
> - [X] HTTP request method: GET
> - [ ] HTTP response data: This is Foo home API.

#### Response

All the HTTP response settings would be managed under key ``http.response``. About the HTTP response configuration, it has 
multiple [strategies](/configure-references/mocked-apis/#mocked_apisapi-namehttpresponsestrategy) for setting the return 
value format. For easily and quickly demonstrating the HTTP response setting, let's use ``string`` strategy right now.

```yaml hl_lines="7-9"
mocked_apis:
  foo_home:
    url: '/foo'
    http:
      request:
        method: 'GET'
      response:
        strategy: string
        value: 'This is Foo home API.'
```

Congratulation! We finish the configuration for mocking API, and we could try to set up the web server to provide the mocking
service!

> - [X] URL path: /foo
> - [X] HTTP request method: GET
> - [X] HTTP response data: This is Foo home API.


## Check configuration validation

If you're meticulous in configuring and developing, **_PyMock-Server_** also provide a command line to help you check your
configuration validation:

```console
mock-api check -p <configuration path>
```

It would check everywhere of configuration and make sure your configuration is valid for running.
