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
generate_cli_args() {
  arg_env_val=$1
  arg_name=$2

  if [ "$arg_env_val" != "" ]; then
    Command_Line_Options="$Command_Line_Options $arg_name $arg_env_val"
  fi
}

generate_cli_args "$Config_Path" "--config"
generate_cli_args "$Web_Framework" "--app-type"
generate_cli_args "$Host_Address" "--bind"
generate_cli_args "$Workers" "--workers"
generate_cli_args "$Log_Level" "--log-level"

echo "Final command line arguments: $Command_Line_Options"

# Run web server for mocking APIs
echo "Start to run server ..."
mock-api run $Command_Line_Options
