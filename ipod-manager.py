"""
==================================================================
 iPod Manager - Main Program
==================================================================
 File        : ipod-manager.py
 Description : The main entry point for the iPod Manager tool.
               Provides a menu-driven interface to manage music
               on iPods running Rockbox and scrobble play history
               to Last.fm.
 Author      : blackbunt
 Created     : 2025-01-26
 License     : GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
 Repository  : https://github.com/blackbunt/ipod-manager
==================================================================
"""

import os
from pathlib import Path
from InquirerPy import inquirer
from modules.file_operations import perform_file_operation, remove_empty_directories
from modules.selection import select_artists, list_artists
from modules.utils import get_music_folder, safely_unmount_ipod
from modules.scrobbler_module import scrobble_log


def find_ipods() -> list:
    """Find connected iPods."""
    ipods = []
    media_path = Path(f"/run/media/{os.getlogin()}")
    if media_path.exists():
        for mount in media_path.iterdir():
            if (mount / "iPod_Control").is_dir():
                ipods.append(mount)
    return ipods

def select_ipod(ipods: list) -> Path:
    """Allows the user to select an iPod from the list of detected devices."""
    choices = [str(ipod) for ipod in ipods]
    if not choices:
        print("No iPod found. Ensure that your iPod is connected.")
        exit(1)
    selected = inquirer.select(
        message="Choose your iPod:",
        choices=choices,
    ).execute()
    return Path(selected)

def copy_music(selected_ipod: Path, copy_all=False):
    """Copies music to the selected iPod."""
    source_dir = get_music_folder()
    artists = list_artists(source_dir)

    if copy_all:
        selected_artists = artists
    else:
        selected_artists = select_artists(artists)

    all_files = []
    for artist in selected_artists:
        artist_path = Path(source_dir) / artist
        for root, _, files in os.walk(artist_path):
            for file in files:
                all_files.append(Path(root) / file)

    perform_file_operation(all_files, selected_ipod / "Music", "copy")

def delete_music(selected_ipod: Path, delete_all=False):
    """Deletes music from the selected iPod."""
    target_dir = selected_ipod / "Music"
    artists = list_artists(target_dir)

    if delete_all:
        selected_artists = artists
    else:
        selected_artists = select_artists(artists)

    confirm = inquirer.confirm(
        message="Are you sure you want to delete the selected artists from your iPod?",
        default=False,
    ).execute()

    if not confirm:
        print("\033[93mDeletion aborted.\033[0m")
        return

    all_files = []
    for artist in selected_artists:
        artist_path = target_dir / artist
        for root, _, files in os.walk(artist_path):
            for file in files:
                all_files.append(Path(root) / file)

    perform_file_operation(all_files, "", "delete")

    # Remove empty directories after deletion
    for artist in selected_artists:
        artist_path = target_dir / artist
        remove_empty_directories(artist_path)
        if artist_path.exists():
            artist_path.rmdir()

def main():
    """Main menu using InquirerPy."""
    ipods = find_ipods()
    selected_ipod = select_ipod(ipods)

    while True:
        action = inquirer.select(
            message="Choose an option:",
            choices=[
                "Copy selected music -> iPod",
                "Copy all music -> iPod",
                "Delete selected music -> iPod",
                "Delete all music on iPod",
                "Scrobble from iPod -> last.fm",
                "Safely unmount iPod",
                "Exit"
            ],
        ).execute()

        if action == "Copy selected music -> iPod":
            copy_music(selected_ipod)
        elif action == "Copy all music -> iPod":
            copy_music(selected_ipod, copy_all=True)
        elif action == "Delete selected music -> iPod":
            delete_music(selected_ipod)
        elif action == "Delete all music on iPod":
            delete_music(selected_ipod, delete_all=True)
        elif action == "Scrobble from iPod -> last.fm":
            scrobble_log(selected_ipod)
        elif action == "Safely unmount iPod":
            safely_unmount_ipod(selected_ipod)
        elif action == "Exit":
            print("\033[92mExiting. See you soon!\033[0m")
            break
        else:
            print("\033[91mInvalid selection, try again.\033[0m")

if __name__ == "__main__":
    main()
