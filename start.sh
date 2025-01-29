#!/bin/bash
# ==================================================================
# iPod Manager - Environment Setup Script
# ==================================================================
# File        : start.sh
# Description : This script ensures the necessary Python virtual
#               environment and dependencies are in place for the
#               iPod Manager application. It also runs the main
#               Python program.
# Author      : blackbunt
# Created     : 2025-01-26
# License     : GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Repository  : https://github.com/blackbunt/ipod-manager
# ==================================================================
# Get script dir and locate venv dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Check and create the virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Virtual environment (.venv) not found. Creating one..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create a virtual environment. Make sure Python 3 is installed."
        exit 1
    fi
    echo "Virtual environment (.venv) created successfully."
fi

# Activate the virtual environment
source .venv/bin/activate

# Check and install missing packages
REQUIRED_PACKAGES=("InquirerPy" "tqdm" "requests")

MISSING_PACKAGES=()
for PACKAGE in "${REQUIRED_PACKAGES[@]}"; do
    if ! pip show "$PACKAGE" &> /dev/null; then
        MISSING_PACKAGES+=("$PACKAGE")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo "The following required packages are missing:"
    for PACKAGE in "${MISSING_PACKAGES[@]}"; do
        echo "  - $PACKAGE"
    done
    echo "Installing missing packages..."
    pip install "${MISSING_PACKAGES[@]}"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install the missing packages. Please check your internet connection or package names."
        exit 1
    fi
fi

# Run the Python script
python ipod-manager.py
