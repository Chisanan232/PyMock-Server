#!/usr/bin/env bash

#####################################################################################################################
#
# Target:
# Automate to :
#   1. get the software version of Python package and output
#   2. build Docker image and tag it by the software version
#   3. release the Docker image to Docker hub with tag
#
# Description:
# Build Docker image and tag it, and release it to Docker hub.
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
           echo "Shell script usage: bash ./scripts/ci/release-docker-image.sh [OPTION] [VALUE]"
           echo " "
           echo "This is a shell script for releasing Docker image to Docker image hub."
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

declare Docker_Image_Tag
generate_image_tag() {
    Docker_Image_Tag=$(bash ./scripts/ci/generate-docker-image-tag.sh -r "$Input_Arg_Release_Type" -p "$Input_Arg_Python_Pkg_Name" -v "$Input_Arg_Software_Version_Format")
    echo "🐳 🖼️ 🏷️  Docker_Image_Tag: $Docker_Image_Tag"
}

declare Docker_Image_Name_With_Tag
generate_docker_image_name_with_tag() {
    is_latest=$1
    if [ "$is_latest" == true ]; then
        echo "ⓥ  Not add tag"
        Docker_Image_Name_With_Tag="$Docker_Image_Name"
    else
        echo "ⓥ ➕ 🏷️  Add tag"
        generate_image_tag
        Docker_Image_Name_With_Tag="$Docker_Image_Name":"$Docker_Image_Tag"
    fi
    echo "🐳 🔖 Docker image name with tag: $Docker_Image_Name_With_Tag"
}

tag_docker_image() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "🕵️   Docker_Image_Name_With_Tag: $Docker_Image_Name_With_Tag"
        echo "It would run command line 'docker tag $Docker_Image_Name_With_Tag chisanan232/$Docker_Image_Name_With_Tag'"
    else
        echo "🏃‍♂    Docker_Image_Name_With_Tag: $Docker_Image_Name_With_Tag"
        docker tag "$Docker_Image_Name_With_Tag" chisanan232/"$Docker_Image_Name_With_Tag"
    fi
}

push_docker_image() {
    if [ "$Running_Mode" == "dry-run" ] || [ "$Running_Mode" == "debug" ]; then
        echo "It would run command line 'docker push chisanan232/$Docker_Image_Name_With_Tag'"
    else
        docker push chisanan232/"$Docker_Image_Name_With_Tag"
    fi
}

tag_docker_image_and_push() {
    is_latest=$1
    echo "Generate tag *latest* for Docker image or not: $is_latest"
    generate_docker_image_name_with_tag "$is_latest"
    tag_docker_image
    push_docker_image
}

final_display() {
    docker images "$Docker_Image_Name"

    echo "🍻 Push image to Docker hub successfully!"
}

# The process what the shell script want to do truly start here
echo "👷  Start to push Docker image to Docker hub ..."

declare use_latest_tag=true
declare use_current_software_ver_tag=false

tag_docker_image_and_push "$use_current_software_ver_tag"
tag_docker_image_and_push "$use_latest_tag"
final_display
