"""
==================================================================
 iPod Manager - Submodule
==================================================================
 File        : selection.py
 Description : Provides functions for discovering connected iPods,
               prompting the user to select an iPod or artists, 
               and listing artists in the music library.
               This submodule is part of the iPod Manager project.
 Author      : blackbunt
 Created     : 2025-01-26
 License     : GPLv3 (https://www.gnu.org/licenses/gpl-3.0.html)
 Repository  : https://github.com/blackbunt/ipod-manager
==================================================================
"""
import os
from pathlib import Path
from typing import List
from InquirerPy import prompt

def find_ipods() -> List[str]:
    """Find connected iPods."""
    ipods = []
    media_path = Path(f"/run/media/{os.getlogin()}")
    for mount in media_path.iterdir():
        if (mount / "iPod_Control").is_dir():
            ipods.append(str(mount))
    return ipods

def select_ipod(ipods: List[str]) -> str:
    """Prompt user to select an iPod."""
    if not ipods:
        print("\033[91mNo iPod found. Please ensure your iPod is connected.\033[0m")
        exit(1)

    questions = [
        {
            "type": "list",
            "name": "ipod",
            "message": "Select an iPod:",
            "choices": ipods,
        }
    ]
    answers = prompt(questions)
    return answers["ipod"]

def list_artists(directory: str) -> List[str]:
    """List artists (top-level directories) in a given directory."""
    return sorted([item.name for item in Path(directory).iterdir() if item.is_dir()])

def select_artists(artists: List[str]) -> List[str]:
    """Prompt user to select one or more artists."""
    if not artists:
        print("\033[91mNo artists found. Exiting.\033[0m")
        exit(1)

    questions = [
        {
            "type": "checkbox",
            "name": "selected_artists",
            "message": "Select artists:",
            "choices": [{"name": artist, "value": artist} for artist in artists],
        }
    ]
    answers = prompt(questions)
    return answers["selected_artists"]
