#!/bin/bash

# Exit on error
set -e

red="\033[31m"
reset="\033[0m"

function error() {
    printf "${red}ERROR:${reset} $1\n"
}

function print_help_and_exit() {
    echo "
This script requires the FSTQ_GCP_PROJECT environment variables to be set.
Example usage:
  export FSTQ_GCP_PROJECT=your-gcp-project
  sh scripts/install.sh
"
    exit 1
}

function assert_set() {
    var_name=$1
    var_value=$2
    if [ -z "$var_value" ]; then
        error "Missing required env variable $var_name"
        print_help_and_exit
    else
        echo "Using $var_name: $var_value"
    fi
}

# assert_set FSTQ_GCP_PROJECT $FSTQ_GCP_PROJECT

# Set the project
# gcloud config set project $FSTQ_GCP_PROJECT

# TODO: create the security rules
# TODO: deploy the functions
