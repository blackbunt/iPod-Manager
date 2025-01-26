"""
==================================================================
 iPod Manager - Submodule
==================================================================
 File        : scrobbler_module.py
 Description : Command-line tool for managing music libraries on 
               iPods running Rockbox, and for scrobbling play
               history to Last.fm.
 Author      : blackbunt
 License     : GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
 Repository  : https://github.com/blackbunt/ipod-manager
==================================================================
"""
import os
import sys
import subprocess
import requests
from pathlib import Path
from tqdm import tqdm
from datetime import datetime, timezone
from InquirerPy import inquirer


def download_rb_scrobbler(download_path: Path):
    """Downloads the latest version of rb-scrobbler from GitHub."""
    url = "https://github.com/blackbunt/rb-scrobbler/releases/latest/download/rb-scrobbler"
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(download_path, "wb") as f:
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total=total_size, unit="B", unit_scale=True, desc="downloading rb-scrobbler") as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    # Make the downloaded file executable
    download_path.chmod(download_path.stat().st_mode | 0o111)

def find_scrobble_log(ipod_path: Path) -> Path:
    """Finds the .scrobbler.log file on the specified iPod."""
    scrobble_log = ipod_path / ".scrobbler.log"
    if scrobble_log.exists():
        return scrobble_log
    else:
        raise FileNotFoundError(f"No .scrobbler.log file found in path: {ipod_path}")

def get_time_offset() -> str:
    """Determines the time offset from UTC in hours."""
    offset_seconds = datetime.now(timezone.utc).astimezone().utcoffset().total_seconds()
    offset_hours = offset_seconds / 3600
    return f"{offset_hours:+.1f}h"

def scrobble_log(ipod_path: Path):
    """Executes the scrobbling of the .scrobbler.log file on the specified iPod."""
    scrobbler_path = Path.home() / ".local" / "bin" / "rb-scrobbler"

    if not scrobbler_path.exists():
        print("rb-scrobbler not found. Please make sure it is installed.")
        return

    scrobbler_log_path = ipod_path / ".scrobbler.log"
    if not scrobbler_log_path.exists():
        print(f"No .scrobbler.log file found in directory {ipod_path}.")
        return

    time_offset = "+1.0h"  # Adjust this according to your timezone

    command = [
        str(scrobbler_path),
        "-f", str(scrobbler_log_path),
        "-o", time_offset,
        "-n", "keep"
    ]

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error while executing rb-scrobbler: {e.stderr}")
        return

    # Ask the user whether to delete the .scrobbler.log file
    delete_log = inquirer.confirm(
        message=f"Do you want to delete the file '{scrobbler_log_path}'?",
        default=False
    ).execute()

    if delete_log:
        try:
            scrobbler_log_path.unlink()
            print(f"File '{scrobbler_log_path}' has been deleted.")
        except Exception as e:
            print(f"Error while deleting the file: {e}")
    else:
        print("The file has been kept.")
