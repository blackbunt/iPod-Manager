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

def get_latest_version() -> dict:
    """Fetches the latest version details of rb-scrobbler from GitHub."""
    url = "https://api.github.com/repos/jeselnik/rb-scrobbler/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_version(version: str, version_file: Path):
    """Saves the current version to a file."""
    with version_file.open("w") as f:
        f.write(version)

def load_version(version_file: Path) -> str:
    """Loads the saved version from a file."""
    if version_file.exists():
        with version_file.open("r") as f:
            return f.read().strip()
    return ""

def get_time_offset() -> str:
    """Determines the time offset from UTC in hours."""
    offset_seconds = datetime.now(timezone.utc).astimezone().utcoffset().total_seconds()
    offset_hours = offset_seconds / 3600
    return f"{offset_hours:+.1f}"

def download_rb_scrobbler(download_path: Path):
    """Downloads the latest version of rb-scrobbler from GitHub."""
    latest_release = get_latest_version()
    latest_version = latest_release["tag_name"]
    version_file = download_path.parent / "rb-scrobbler-version"
    saved_version = load_version(version_file)

    if saved_version == latest_version and download_path.exists():
        print(f"You already have the latest version: {latest_version}")
        return

    platform_map = {
        "linux": "rb-scrobbler-linux-amd64",
        "darwin": "rb-scrobbler-darwin-amd64",
        "windows": "rb-scrobbler-windows-amd64.exe",
    }

    system = os.uname().sysname.lower()
    asset_name = platform_map.get(system)

    if not asset_name:
        raise ValueError(f"Unsupported platform: {system}")

    asset_url = next(
        (
            asset["browser_download_url"]
            for asset in latest_release["assets"]
            if asset_name in asset["name"]
        ),
        None,
    )

    if not asset_url:
        raise FileNotFoundError(f"Asset not found for platform: {system}")

    response = requests.get(asset_url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    if total_size == 0:
        raise ValueError("Download failed: The content is empty.")

    with open(download_path, "wb") as f:
        with tqdm(total=total_size, unit="B", unit_scale=True, desc="downloading rb-scrobbler") as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    # Make the downloaded file executable
    download_path.chmod(download_path.stat().st_mode | 0o111)

    # Verify that the file exists and is executable
    if not (download_path.exists() and os.access(download_path, os.X_OK)):
        raise FileNotFoundError("Downloaded rb-scrobbler is not executable or missing.")

    # Save the downloaded version
    save_version(latest_version, version_file)
    print(f"rb-scrobbler {latest_version} has been downloaded and verified.")

def scrobble_log(ipod_path: Path):
    """Executes the scrobbling of the .scrobbler.log file on the specified iPod."""
    scrobbler_path = Path.home() / ".local" / "bin" / "rb-scrobbler"

    # Check if rb-scrobbler exists
    if not scrobbler_path.exists():
        print("rb-scrobbler not found.")
        download_choice = inquirer.confirm(
            message="rb-scrobbler is missing. Do you want to download it now?",
            default=True
        ).execute()

        if download_choice:
            try:
                download_rb_scrobbler(scrobbler_path)
                print("rb-scrobbler has been downloaded successfully.")
            except Exception as e:
                print(f"Error while downloading rb-scrobbler: {e}")
                return
        else:
            print("rb-scrobbler is required to proceed. Exiting.")
            return

    # Verify that rb-scrobbler exists and is executable
    if not (scrobbler_path.exists() and os.access(scrobbler_path, os.X_OK)):
        print("Error: rb-scrobbler is not executable or missing after download.")
        return

    # Check for updates
    version_file = scrobbler_path.parent / "rb-scrobbler-version"
    latest_release = get_latest_version()
    latest_version = latest_release["tag_name"]
    saved_version = load_version(version_file)

    if saved_version != latest_version:
        print(f"A new version of rb-scrobbler is available: {latest_version} (current: {saved_version})")
        update_choice = inquirer.confirm(
            message="Do you want to update to the latest version?",
            default=True
        ).execute()

        if update_choice:
            try:
                download_rb_scrobbler(scrobbler_path)
                print("rb-scrobbler has been updated successfully.")
            except Exception as e:
                print(f"Error while updating rb-scrobbler: {e}")
                return

    scrobbler_log_path = ipod_path / ".scrobbler.log"
    if not scrobbler_log_path.exists():
        print(f"No .scrobbler.log file found in directory {ipod_path}.")
        return

    time_offset = get_time_offset()

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

if __name__ == "__main__":
    ipod_path = Path(input("Enter the path to your iPod: ").strip())
    if not ipod_path.exists():
        print("The specified path does not exist.")
    else:
        scrobble_log(ipod_path)

