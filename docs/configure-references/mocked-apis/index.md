# Mocked API settings

This configuration section is the major function because here settings would decide how your mocked API works.

## ``mocked_apis``

Manage the API detail settings. The elements in it would be key-value map format. The key means the common feature or API
name. The value means the detail settings of the common feature or API name.

So what is the common feature? **_PyMock-Server_** provides some feature to let developers could to more convenience and clear
of configuring mocked API. Following are the common features it provides currently:

* [Basic information](#mocked_apisbase)


### ``template``

The template settings information of entire configuration for all mocked APIs. It would apply this section settings for
scanning or finding the configuration files about the setting details of every mocked APIs.

[Here](/configure-references/mocked-apis/template) is the configuration details.


### ``base``

The basic information of all APIs. It would apply this section settings for all APIs.

[Here](/configure-references/mocked-apis/base) is the configuration details.


### ``<API name>``

The API you target to mock. The API name must be unique.

[Here](/configure-references/mocked-apis/apis) is the configuration details.
