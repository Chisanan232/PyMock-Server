# Mocked API

This configuration section is the major function because here settings would decide how your mocked API works.


## ``mocked_apis.<API name>``

The API you target to mock. The API name must be unique.

About the detail settings of API, it has 3 major sections:

* API URL ([config](/configure-references/mocked-apis/apis/url))

    All settings about URL path.

* API HTTP request ([config](/configure-references/mocked-apis/apis/http/request))

    All settings about how it should handle HTTP request.

* API HTTP response ([config](/configure-references/mocked-apis/apis/http/response))

    All settings about how it should return HTTP response.
