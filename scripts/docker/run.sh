#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Provide for developer who want to set up a web server in a Docker container.
#
# Description:
# Set up and run web server with Python web framework by server gateway interface (WSGI or ASGI).
#
# Allowable argument:
# Nothing.
#
#####################################################################################################################

# Check the environment variables and set default value to them if it's empty
echo "Start to check command line tool arguments ..."

# Configuration settings
# Configuration file
Config_Path=$CONFIG_PATH

# Web framework
Web_Framework=$WEB_FRAMEWORK

# Web server
#Host_Address=$HOST_ADDRESS
Host_Address="0.0.0.0:9672"
Workers=$WORKERS
Log_Level=$LOG_LEVEL

echo "ℹ️ All parameters:"
echo "    🗃️ configuration file setting "
echo "        📄 configuration path: $Config_Path"
echo "    🤖️ web framework "
echo "        📄 Python web library: $Web_Framework"
echo "    🖥️️ web server "
echo "        📄 host: $Host_Address"
echo "        📄 workers amount to process requests: $Workers"
echo "        📄 log level: $Log_Level"

Command_Line_Options=""
generate_cli_args_if_not_empty() {
  arg_name=$1
  arg_env_val=$2

  if [ "$arg_env_val" != "" ]; then
    Command_Line_Options="$Command_Line_Options $arg_name $arg_env_val"
  fi
}

generate_cli_args_if_not_empty "--config" "$Config_Path"
generate_cli_args_if_not_empty "--app-type" "$Web_Framework"
generate_cli_args_if_not_empty "--bind" "$Host_Address"
generate_cli_args_if_not_empty "--workers" "$Workers"
generate_cli_args_if_not_empty "--log-level" "$Log_Level"

echo "⚙️ Final command line arguments: $Command_Line_Options"

# Run web server for mocking APIs
echo "+++++++++++++ 🍻 Start to run server +++++++++++++"
fake rest-server run $Command_Line_Options
