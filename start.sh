#!/bin/bash
#
#This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
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
