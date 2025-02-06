# Subcommand ``rest-server`` usage

If you try to mock HTTP server which through REST API to communicate between client side and server side, subcommand 
``rest-server`` must can help you to do that easily and quickly.

```console
>>> fake rest-server <option>
```

This subcommand line doesn't have any options but have multiple subcommand lines for processing different operation.

## subcommand [``run``](./subcmd-run.md)

Set up a REST API server.


## subcommand [``get``](./subcmd-get.md)

Get the details by the specific API from configuration.


## subcommand [``add``](./subcmd-add.md)

Add new API into configuration.


## subcommand [``check``](./subcmd-check.md)

Check the validation of configuration.


## subcommand [``sample``](./subcmd-sample.md)

Display the valid example configuration.


## subcommand [``pull``](./subcmd-pull.md)

Pull the API documentation detail setting from document host or document configuration as PyFake-API-Server configuration.
