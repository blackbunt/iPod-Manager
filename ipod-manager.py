import os
from pathlib import Path
from typing import List
from InquirerPy import prompt
import subprocess
from tqdm import tqdm

def get_music_folder() -> str:
    """Get the music folder dynamically using xdg-user-dir."""
    result = subprocess.run(["xdg-user-dir", "MUSIC"], capture_output=True, text=True)
    music_dir = result.stdout.strip()

    # Fallback to ~/Musik if xdg-user-dir fails
    if not music_dir or not Path(music_dir).is_dir():
        music_dir = str(Path.home() / "Musik")  # Default for German systems

    return music_dir

def find_ipods() -> List[str]:
    """Find connected iPods."""
    ipods = []
    media_path = Path(f"/run/media/{os.getlogin()}")
    for mount in media_path.iterdir():
        if (mount / "iPod_Control").is_dir():
            ipods.append(str(mount))
    return ipods

def select_ipod(ipods: List[str]) -> str:
    """Prompt user to select an iPod using InquirerPy."""
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
    """Prompt user to select one or more artists using InquirerPy."""
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

def perform_file_operation(file_list: List[Path], target: str, mode: str):
    """Perform file operations (copy or delete) with tqdm progress tracking."""
    total_size = sum(file.stat().st_size for file in file_list) if mode == "copy" else len(file_list)

    if mode == "copy":
        with tqdm(total=total_size, desc="Copying songs", unit="MB", unit_scale=True) as progress:
            for file in file_list:
                relative_path = file.relative_to(file.parents[2])
                target_file = Path(target) / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)

                result = subprocess.run([
                    "rsync", "-ah", str(file), str(target_file)
                ], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                if result.returncode != 0:
                    print(f"\033[91mError copying {file.name}: {result.stderr.decode()}\033[0m")
                progress.update(file.stat().st_size)
    elif mode == "delete":
        with tqdm(total=total_size, desc="Deleting songs", unit="songs") as progress:
            for file in file_list:
                result = subprocess.run([
                    "rm", str(file)
                ], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                if result.returncode != 0:
                    print(f"\033[91mError deleting {file.name}: {result.stderr.decode()}\033[0m")
                progress.update(1)

def copy_music():
    """Copy music to iPod."""
    source_dir = get_music_folder()
    artists = list_artists(source_dir)

    selected_artists = select_artists(artists)
    ipods = find_ipods()
    selected_ipod = select_ipod(ipods)

    all_files = []
    for artist in selected_artists:
        artist_path = Path(source_dir) / artist
        for root, _, files in os.walk(artist_path):
            for file in files:
                all_files.append(Path(root) / file)

    perform_file_operation(all_files, Path(selected_ipod) / "Music", "copy")

def delete_music():
    """Delete music by artist from iPod."""
    ipods = find_ipods()
    selected_ipod = select_ipod(ipods)
    target_dir = Path(selected_ipod) / "Music"

    artists = list_artists(target_dir)
    selected_artists = select_artists(artists)

    confirm_question = [
        {
            "type": "confirm",
            "name": "confirm",
            "message": "Are you sure you want to delete the selected artist(s) from the iPod?",
            "default": False,
        }
    ]
    confirm = prompt(confirm_question)
    if not confirm["confirm"]:
        print("\033[93mDeletion cancelled.\033[0m")
        exit(1)

    all_files = []
    for artist in selected_artists:
        artist_path = target_dir / artist
        for root, _, files in os.walk(artist_path):
            for file in files:
                all_files.append(Path(root) / file)

    perform_file_operation(all_files, "", "delete")

def main():
    """Main menu using InquirerPy."""
    questions = [
        {
            "type": "list",
            "name": "action",
            "message": "Select an action:",
            "choices": ["Copy music to iPod", "Delete music from iPod"],
        }
    ]
    answers = prompt(questions)

    if answers["action"] == "Copy music to iPod":
        copy_music()
    elif answers["action"] == "Delete music from iPod":
        delete_music()
    else:
        print("\033[91mInvalid selection. Exiting.\033[0m")
        exit(1)

if __name__ == "__main__":
    main()
