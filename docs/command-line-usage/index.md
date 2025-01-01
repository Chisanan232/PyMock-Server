# Command line usages

Currently, it doesn't have any options could use of command line ``mock`` without subcommand. The only one option which
is useful is ``--version`` for checking current version info in your runtime environment.

```console
>>> mock <option>
```


## ``--version``

Show to details about version info in current runtime environment. The version info includes its dependencies (web 
framework, server gateway interface) version info.

```shell
>>> mock --version
########## PyMock-Server: ##########
pymock-server (version 0.2.0)

############ Web server: ############
flask (version: 3.0.3)
fastapi (version: 0.115.6)

##### Server gateway interface: #####
gunicorn (version: 23.0.0)
uvicorn (version: 0.32.1)
```
