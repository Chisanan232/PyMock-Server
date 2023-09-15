#!/usr/bin/env bash

set -ex
runtime_os=$1

declare -a init_tests
declare -a utils_tests
declare -a model_tests
declare -a model_api_config_tests
declare -a server_tests
declare -a server_application_tests
declare -a server_sgi_tests
declare -a command_tests
declare -a subcommand_run_tests
declare -a subcommand_add_tests
declare -a subcommand_check_tests
declare -a subcommand_get_tests
declare -a subcommand_sample_tests

getalltests() {
    # shellcheck disable=SC2207
    # shellcheck disable=SC2010
    declare -a testpatharray=( $(ls -F "$1" | grep -v '/$' | grep -v '__init__.py' | grep -v 'test_config.py' | grep -v -E '^_[a-z_]{1,64}.py' | grep -v '__pycache__'))

    declare -a alltestpaths
    for (( i = 0; i < ${#testpatharray[@]}; i++ )) ; do
        alltestpaths[$i]=$1${testpatharray[$i]}
    done

    if echo "$1" | grep -q "utils";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        utils_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "api_config";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        model_api_config_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "model";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        model_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "sgi";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        server_sgi_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "application";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        server_application_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "server";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        server_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "run";  # /command/run
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        subcommand_run_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "add";  # /command/add
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        subcommand_add_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "check";  # /command/check
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        subcommand_check_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "get";  # /command/get
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        subcommand_get_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "sample";  # /command/sample
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        subcommand_sample_tests=${alltestpaths[@]}
    elif echo "$1" | grep -q "command";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        command_tests=${alltestpaths[@]}
    else
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        init_tests=${alltestpaths[@]}
    fi
}

init_path=./test/unit_test/
utils_path=./test/unit_test/_utils/
model_path=./test/unit_test/model/
model_api_config_path=./test/unit_test/model/api_config/
server_path=./test/unit_test/server/
server_application_path=./test/unit_test/server/application/
server_sgi_path=./test/unit_test/server/sgi/
command_path=./test/unit_test/command/
subcommand_run_path=./test/unit_test/command/run/
subcommand_add_path=./test/unit_test/command/add/
subcommand_check_path=./test/unit_test/command/check/
subcommand_get_path=./test/unit_test/command/get/
subcommand_sample_path=./test/unit_test/command/sample/

getalltests $init_path
getalltests $utils_path
getalltests $model_path
getalltests $model_api_config_path
getalltests $server_path
getalltests $server_application_path
getalltests $server_sgi_path
getalltests $command_path
getalltests $subcommand_run_path
getalltests $subcommand_add_path
getalltests $subcommand_check_path
getalltests $subcommand_get_path
getalltests $subcommand_sample_path

dest=( "${init_tests[@]} ${utils_tests[@]} ${model_tests[@]} ${model_api_config_tests[@]} ${server_tests[@]} ${server_application_tests[@]} ${server_sgi_tests[@]} ${command_tests[@]} ${subcommand_run_tests[@]} ${subcommand_add_tests[@]} ${subcommand_check_tests[@]} ${subcommand_get_tests[@]} ${subcommand_sample_tests[@]}" )

if echo "$runtime_os" | grep -q "windows";
then
    printf "${dest[@]}" | jq -R .
elif echo "$runtime_os" | grep -q "unix";
then
    printf '%s\n' "${dest[@]}" | jq -R . | jq -cs .
else
    printf 'error' | jq -R .
fi
