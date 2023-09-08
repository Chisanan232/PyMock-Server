# Base

This configuration section is the major function because here settings would decide how your mocked API works.


## ``mocked_apis.base``

The basic information of all APIs. It would apply this section settings for all APIs.


## ``mocked_apis.base.url``

The URL basic information of all APIs. It would apply the URL path to all API path. Let's give you an example to demonstrate:

```yaml
mocked_apis:
  base:
    url: '/test/v1'
```

Base on above settings to configure your mocked API, you would need to add the URL path ``/test/v1`` in font of the URL
path of all APIs. So your HTTP request URL would be like as below:

```console
http://127.0.0.1:9672/test/v1<API path>
```

And it's an empty string if you omit this setting. In the other words, you could use the API URL path you set directly.
