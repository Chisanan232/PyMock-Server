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
#  -r [Release type]              Release type of project. Different release type it would get different version format. [options: python-package]
#  -p [Python package name]       The Python package name. It will use this naming to get the package info module (__pkg_info__.py) to get the version info.
#  -v [Version format]            Which version format you should use. [options: general-2, general-3, date-based]
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
    if [ "$OPTARG" == "r" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
        echo "  -r [Release type]              Release type of project. Different release type it would get different version format. [options: python-package]"
    fi
    if [ "$OPTARG" == "p" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
        echo "  -p [Python package name]       The Python package name. It will use this naming to get the package info module (__pkg_info__.py) to get the version info."
    fi
    if [ "$OPTARG" == "v" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
        echo "  -v [Version format]            Which version format you should use. [options: general-2, general-3, date-based]"
    fi
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
         "r")    # Release type
           Input_Arg_Release_Type=$OPTARG
           ;;
         "p")    # Python package name
           Input_Arg_Python_Pkg_Name=$OPTARG
           ;;
         "v")    # Software version format
           Input_Arg_Software_Version_Format=$OPTARG
           ;;
         "d")    # Dry run
           Running_Mode=$OPTARG
           ;;
         ?)
           echo "Invalid command line argument. Please use option *h* to get more details of argument usage."
           exit
           ;;
     esac
done

set_git_config() {
    git config --global user.name github-actions[bot]
}

declare New_Release_Version
generate_version_info() {
    New_Release_Version=$(bash ./scripts/ci/generate-software-version.sh -r "$Input_Arg_Release_Type" -p "$Input_Arg_Python_Pkg_Name" -v "$Input_Arg_Software_Version_Format" -d "$Running_Mode")
    echo "🐍 Software version: $New_Release_Version"
}

set_default_version_as_latest() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "👨‍💻 This is debug mode, doesn't really set the default version to document."
        echo "👨‍💻 Under running command line: poetry run mike set-default --push latest"
    else
        poetry run mike set-default --push latest
    fi

    echo "🍻 Set the documentation content default version as 'latest' successfully!"
}

push_new_version_to_document_server() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "👨‍💻 This is debug mode, doesn't really deploy the new version to document."
        echo "👨‍💻 Under running command line: poetry run mike deploy --push --update-aliases $New_Release_Version latest"
    else
        poetry run mike deploy --push --update-aliases "$New_Release_Version" latest
    fi

    echo "🍻 Push new version documentation successfully!"
}

# The process what the shell script want to do truly start here
echo "👷  Start to push new version documentation ..."

set_git_config
generate_version_info
push_new_version_to_document_server
set_default_version_as_latest

echo "👷  Deploy new version documentation successfully!"
