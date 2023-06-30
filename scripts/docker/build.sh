#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Provide for developer who want to set up a web server in a Docker container.
#
# Description:
# Set up and run web server with Python web framework by server gateway interface (WSGI or ASGI).
#
# Allowable options:
#  -r [Release type]              Release type of project. Different release type it would get different version format. [options: python-package]
#  -p [Python package name]       The Python package name. It will use this naming to get the package info module (__pkg_info__.py) to get the version info.
#  -v [Version format]            Which version format you should use. [options: general-2, general-3, date-based]
#  -i [Docker image name]         Set the naming to the Docker image this shell will build.
#  -d [Run mode]                  Running mode. Set 'dry-run' or 'debug' to let it only show log message without exactly working. [options: general, dry-run, debug]
#  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]
#
#####################################################################################################################

while getopts "r:p:v:i:d:h:?" argv
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
         "i")    # Use this to name Docker image it will build
           Docker_Image_Name=$OPTARG
           ;;
         "d")    # Dry run
           Running_Mode=$OPTARG
           ;;
         "h")    # Help for display all usage of each arguments
           echo "Shell script usage: bash ./scripts/docker/build.sh [OPTION] [VALUE]"
           echo " "
           echo "This is a shell script for building Docker image with software version which be get from package info module (__pkg_info__) from Python package."
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
           if [ "$OPTARG" == "i" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -i [Docker image name]         Set the naming to the Docker image this shell will build."
           fi
           if [ "$OPTARG" == "d" ] || [ "$OPTARG" == "h" ] || [ "$OPTARG" == "all" ]; then
               echo "  -d [Run mode]                  Running mode. Set 'dry-run' or 'debug' to let it only show log message without exactly working. [options: general, dry-run, debug]"
           fi
           echo "  -h [Argument]                  Show this help. You could set a specific argument naming to show the option usage. Empty or 'all' would show all arguments usage. [options: r, p, v, i, d, h]"
           exit
           ;;
         ?)
           echo "Invalid command line argument. Please use option *h* to get more details of argument usage."
           exit
           ;;
     esac
done

# # # # From the PEP440: Software version style rule
# # #
# # # The version setting 1: version format
# # Simple “major.minor” versioning: (general-2)
# 0.1,   0.2,   0.3,   1.0,   1.1
# # Simple “major.minor.micro” versioning: (general-3)
# 1.0.0,   1.0.1,   1.0.2,   1.1.0
# # Date based releases, using an incrementing serial within each year, skipping zero: (date-based)
# 2012.1,   2012.2,  ...,   2012.15,   2013.1,   2013.2
# # # The version setting 2: version evolution
# # “major.minor” versioning with alpha, beta and candidate pre-releases: (sema)
# 0.9,   1.0a1,   1.0a2,   1.0b1,   1.0rc1,   1.0
# # “major.minor” versioning with developmental releases, release candidates and post-releases for minor corrections: (dev)
# 0.9,   1.0.dev1,   1.0.dev2,   1.0.dev3,   1.0c1,   1.0,   1.0.post1,   1.1.dev1
#Input_Arg_Software_Version_Format=$3

declare Software_Version_Reg
declare Python_Version_Reg
generate_version_regex() {
    if [ "$Input_Arg_Release_Type" == 'python-package' ]; then

        if [ "$Input_Arg_Python_Pkg_Name" == "" ]; then
            echo "❌ The argument 'Input_Arg_Python_Pkg_Name' (second argument) cannot be empty if option 'Input_Arg_Release_Type' (first argument) is 'python-package'."
            exit 1
        fi

        declare version_reg
        if [ "$Input_Arg_Software_Version_Format" == "general-2" ]; then
            version_reg="[0-9]\.[0-9]"
        elif [ "$Input_Arg_Software_Version_Format" == "general-3" ]; then
            version_reg="[0-9]\.[0-9]\.[0-9]"
        elif [ "$Input_Arg_Software_Version_Format" == "date-based" ]; then
            version_reg="[0-9]{4}\.([0-9]{1,})+"
        else
            # Default value
            version_reg="[0-9]\.[0-9]\.[0-9]"
        fi

        Software_Version_Reg="$version_reg*([\.,-]*([a-zA-Z]{1,})*([0-9]{0,})*){0,}"
        Python_Version_Reg="__version__ = \"$Software_Version_Reg\""

    fi
}

declare New_Release_Version    # This is the return value of function 'generate_new_version_as_tag'
generate_new_version_as_tag() {
    project_type=$1
    if [ "$project_type" == "python" ]; then
        echo "🔎 🐍 📦  Get the new version info from Python package."
        New_Release_Version=$(cat ./"$Input_Arg_Python_Pkg_Name"/__pkg_info__.py | grep -E "$Python_Version_Reg" | grep -E -o "$Software_Version_Reg")
    fi
}

build_docker_image() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "🕵️   New_Release_Version: $New_Release_Version"
        echo "It would run command line 'docker build ./ -t $Docker_Image_Name:v$New_Release_Version'"
    else
        echo "🏃‍♂️    New_Release_Version: $New_Release_Version"
        docker build ./ -t "$Docker_Image_Name":v"$New_Release_Version"
    fi
}

final_display() {
    docker images "$Docker_Image_Name"

    echo "🍻 Build successfully!"
}

# The process what the shell script want to do truly start here
echo "Start to check command line tool arguments ..."

generate_version_regex
generate_new_version_as_tag "python"
build_docker_image
final_display
