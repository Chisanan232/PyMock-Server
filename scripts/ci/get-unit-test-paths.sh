#!/usr/bin/env bash

set -ex
runtime_os=$1

declare -a init_tests
declare -a utils_tests
declare -a model_tests
declare -a server_tests
declare -a server_sgi_tests
declare -a command_tests
declare -a subcommand_run_tests
declare -a subcommand_check_tests

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
    elif echo "$1" | grep -q "check";  # /command/check
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        subcommand_check_tests=${alltestpaths[@]}
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
server_path=./test/unit_test/server/
server_sgi_path=./test/unit_test/server/sgi/
command_path=./test/unit_test/command/
subcommand_run_path=./test/unit_test/command/run/
subcommand_check_path=./test/unit_test/command/check/

getalltests $init_path
getalltests $utils_path
getalltests $model_path
getalltests $server_path
getalltests $server_sgi_path
getalltests $command_path
getalltests $subcommand_run_path
getalltests $subcommand_check_path

dest=( "${init_tests[@]} ${utils_tests[@]} ${model_tests[@]} ${server_tests[@]} ${server_sgi_tests[@]} ${command_tests[@]} ${subcommand_run_tests[@]} ${subcommand_check_tests[@]}" )

if echo "$runtime_os" | grep -q "windows";
then
    printf "${dest[@]}" | jq -R .
elif echo "$runtime_os" | grep -q "unix";
then
    printf '%s\n' "${dest[@]}" | jq -R . | jq -cs .
else
    printf 'error' | jq -R .
fi
