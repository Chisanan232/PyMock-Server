#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Automate to get the software version of Python package.
#
# Description:
# Use the version regex to get the software version of Python package, and output it.
#
# Allowable options:
#  -d [Run mode]                  Running mode. Set 'dry-run' or 'debug' to let it only show log message without exactly working. [options: general, dry-run, debug]
#  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]
#
#####################################################################################################################

show_help() {
    echo "Shell script usage: bash ./scripts/ci/generate-software-version.sh [OPTION] [VALUE]"
    echo " "
    echo "This is a shell script for generating tag by software version which be recorded in package info module (__pkg_info__) from Python package for building Docker image."
    echo " "
    echo "options:"
    echo "  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, d]"
}

# Show help if no arguments provided
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Handle arguments
if [ $# -gt 0 ]; then
    case "$1" in
        -h|--help)    # Help for display all usage of each arguments
            show_help
            exit 0
            ;;
    esac
fi

while getopts "r:p:v:d:?" argv
do
     case $argv in
         "d")    # Dry run
           Running_Mode=$OPTARG
           ;;
         ?)
           echo "Invalid command line argument. Please use option *h* to get more details of argument usage."
           exit
           ;;
     esac
done

sync_code() {
    # note: https://github.com/jimporter/mike?tab=readme-ov-file#deploying-via-ci
    git fetch origin gh-pages --depth=1
}

set_git_config() {
    git config --global user.name github-actions[bot]
    git config --global user.email chi10211201@cycu.org.tw
}

declare Latest_Version_Alias_Name="latest"

push_new_version_to_document_server() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "👨‍💻 This is debug mode, doesn't really deploy the new version to document."
        echo "👨‍💻 Under running command line: poetry run mike deploy --push $Latest_Version_Alias_Name"
    else
#        poetry run mike deploy --message "[bot] Deploy a new version documentation." --push --update-aliases "$New_Release_Version" latest
        poetry run mike deploy --push $Latest_Version_Alias_Name
    fi

    echo "🍻 Push new version documentation successfully!"
}

# The process what the shell script want to do truly start here
echo "👷  Start to push new version documentation ..."

sync_code
set_git_config
push_new_version_to_document_server

echo "👷  Deploy new version documentation successfully!"
