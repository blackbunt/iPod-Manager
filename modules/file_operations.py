'''
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''
import os
import subprocess
from pathlib import Path
from tqdm import tqdm
from typing import List

def perform_file_operation(file_list: List[Path], target: str, mode: str):
    """Perform file operations (copy or delete) with tqdm progress tracking."""
    total_size = sum(file.stat().st_size for file in file_list) if mode == "copy" else len(file_list)

    if mode == "copy":
        with tqdm(total=total_size, desc="Copying songs", unit="MB", unit_scale=True) as progress:
            for file in file_list:
                relative_path = file.relative_to(file.parents[2])
                target_file = Path(target) / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)

                result = subprocess.run(
                    ["rsync", "-ah", str(file), str(target_file)],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                if result.returncode != 0:
                    print(f"\033[91mError copying {file.name}: {result.stderr.decode()}\033[0m")
                progress.update(file.stat().st_size)
    elif mode == "delete":
        with tqdm(total=total_size, desc="Deleting songs", unit="songs") as progress:
            for file in file_list:
                result = subprocess.run(
                    ["rm", str(file)],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE
                )

                if result.returncode != 0:
                    print(f"\033[91mError deleting {file.name}: {result.stderr.decode()}\033[0m")
                progress.update(1)

def remove_empty_directories(directory: Path):
    """Recursively remove empty directories."""
    for root, dirs, _ in os.walk(directory, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            if not any(dir_path.iterdir()):
                dir_path.rmdir()