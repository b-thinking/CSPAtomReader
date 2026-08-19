#!/usr/bin/env bash
# Author: Jose M. Albarran (Oracle)

# This script requires to be executed with 'source'
(return 0 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "You must execute this script with 'source'. Sample:"
    echo "source $0"
    exit 1
fi


# Load environment variables
source .env
# Set default values for environment variables
OCI_PROFILE=${OCI_PROFILE:-"DEFAULT"}

# Install python version using Pyenv

PYTHON_VERSION='3.12' # Set required python version
VIRTUAL_ENV="csp" # Set venv name
PYTHON_VERSION_GREP="^$(echo $PYTHON_VERSION|sed 's/\./\\./g')\.\d*\$"

# Install python 3.12 (use pyenv to install python versions)
echo "Checking python 3.12 installation and install if needed"
pyenv versions --bare | grep '^3\.12\.\d*$' || pyenv install 3.12

# Set python 3.12 as default (use last available version)
PYTHON_VERSION=$(pyenv versions --bare | grep '^3\.12\.\d*$' | sort -V | tail -n 1)
rm .python-version
pyenv local $PYTHON_VERSION
echo "Using Python version: $PYTHON_VERSION"


# Create venv environment. We copy the files for avoiding problems with Onedrive (it does not allow to create symlinks)
# python -m venv .venv --copies
echo "Creating environment"
rm -rf .venv
python -m venv .venv


# Activate venv environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements in environment"
pip install --upgrade pip
pip install -r requirements.txt







