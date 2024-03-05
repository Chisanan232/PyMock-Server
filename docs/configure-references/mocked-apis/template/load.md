# Template loading setting

## ``mocked_apis.template.load_config``

The section about some detail settings of loading configuration.


### ``includes_apis``

It accepts a boolean type value. If it's ``True``, it would include the mocked APIs which is in section ``mocked_apis.apis``
to load configuration, and vice versa.

!!! note "For scanning file"

    No matter it's ``True`` or ``False``, it would try to load mocked APIs setting to configuration by scanning file.

### ``order``

It accepts a list type value. It could adjust the loading order. In **_PyMock-API_** realm, it has 3 ways to load configuration:

* ``apis``

    Load the mocked APIs from the section ``mocked_apis.apis``.

* ``apply``

    Load the specific mocked APIs by the section ``mocked_apis.template.apply.api``.

* ``file``

    Load the mocked APIs by scanning file.

!!! nore "Besides controlling order, also can control which way to load"

    In addition to controlling the order to load configuration, it depends on the 
    list to load configuration one by one, so it also could use this option to control
    which ways you want it to load ONLY.
