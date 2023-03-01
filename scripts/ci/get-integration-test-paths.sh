#!/usr/bin/env bash

set -ex
runtime_os=$1

declare -a init_tests
declare -a utils_tests
declare -a crawler_tests

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
    elif echo "$1" | grep -q "crawler";
    then
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        crawler_tests=${alltestpaths[@]}
    else
        # shellcheck disable=SC2124
        # shellcheck disable=SC2178
        init_tests=${alltestpaths[@]}
    fi
}

init_path=./test/integration_test/
utils_path=./test/integration_test/_utils/
#crawler_path=./test/integration_test/crawler/

getalltests $init_path
getalltests $utils_path
#getalltests $crawler_path

dest=( "${init_tests[@]} ${utils_tests[@]} ${crawler_tests[@]}" )

if echo "$runtime_os" | grep -q "windows";
then
    printf "${dest[@]}" | jq -R .
elif echo "$runtime_os" | grep -q "unix";
then
    printf '%s\n' "${dest[@]}" | jq -R . | jq -cs .
else
    printf 'error' | jq -R .
fi
