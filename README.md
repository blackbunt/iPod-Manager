# iPod Manager

## Overview
The **iPod Manager** is a command-line tool for seamless management of your music library, your iPod and Last.fm directly from the shell. It allows users to efficiently copy, delete, and manage music files while also scrobbling play history to [Last.fm](https://www.last.fm).

You need an iPod running with [Rockbox](https://www.rockbox.org/) to use this program.
## TL;DR
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ipod-manager.git
   cd ipod-manager
   ```
2. Run the program with:
   ```bash
   ./start.sh
   ```
3. Make sure the following tools are installed: `rsync`, `lsblk`, `lsof`, and `udisksctl`. The script will handle everything else (virtual environment setup, Python dependencies, and downloading the `rb-scrobbler` binary).
4. The music library must follow this structure: `{artist}/{album}/{tracks}`. The program uses the system folder for Music.
5. You can only manage music artist-wise to keep operations simple.
6. The program filters and processes `.flac`, `.mp3`, and `.m4a` files, with copying operations handled by `rsync` for efficiency.

## Key Features
- Copy selected or all music from your local library to an iPod.
- Delete selected or all music from the iPod.
- Scrobble play history from `.scrobbler.log` to Last.fm.
- Safely unmount the iPod to prevent file system corruption.
- Automatically detects connected iPods running Rockbox.
- Fully automates the setup process for dependencies and required binaries.

## Usage Scenarios
### 1. Copy Selected Music to iPod
Easily transfer specific artists or albums from your local music library to your iPod.

Select "Copy selected music -> iPod" from the menu, choose the desired artists from your local music folder, and the tool will copy the selected music to the iPod's `Music` directory.

### 2. Copy All Music to iPod
Transfer your entire local music library to your iPod in one step.

Select "Copy all music -> iPod" from the menu, and the tool will copy all music files to the iPod's `Music` directory.

### 3. Delete Selected Music from iPod
Remove specific artists or albums from the iPod's music library.

Select "Delete selected music -> iPod" from the menu, choose the artists or albums to delete, and confirm the deletion when prompted.

### 4. Delete All Music from iPod
Clear the entire music library on your iPod.

Select "Delete all music on -> iPod" from the menu and confirm the deletion when prompted.

### 5. Scrobble Plays to Last.fm
Upload play history from the iPod's `.scrobbler.log` file to Last.fm.

The program automatically downloads and sets up the `rb-scrobbler` binary if not already present. Select "Scrobble from iPod -> Last.fm" from the menu, and the tool uploads play data to Last.fm, asking whether to delete the `.scrobbler.log` file afterward.

### 6. Safely Unmount iPod
Unmount the iPod safely.

Select "Safely unmount iPod" from the menu, and the tool unmounts the iPod, notifying you if any processes are blocking the unmount.

## Installation

### Requirements
- Linux system
- Rockbox installed on your iPod
- Installed system tools:
  - `rsync`
  - `lsblk`
  - `lsof`
  - `udisksctl`

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ipod-manager.git
   cd ipod-manager
   ```

2. Run the program directly using the provided script:
   ```bash
   ./start.sh
   ```

The `start.sh` script:
- Automatically creates and activates a virtual environment.
- Installs any missing Python dependencies (`InquirerPy`, `tqdm`, `requests`).
- Downloads and sets up the `rb-scrobbler` binary.

## Music Library Requirements
- The music library must follow this structure: `{system musicfolder}/{artist}/{album}/{tracks}`.
- Only `.flac`, `.mp3`, and `.m4a` files are processed.
- Music is managed artist-wise for simplicity.

## License
This project is licensed under the [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html) due to its dependency on the `rb-scrobbler` binary. By using this program, you agree to comply with the terms of the GPLv3 license.

### Acknowledgments
This project uses the `rb-scrobbler` binary for Last.fm scrobbling. The binary is licensed under the [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html).

Source code for `rb-scrobbler` is available here:
- [Original Repository](https://github.com/jeselnik/rb-scrobbler)
- [Forked Repository (if applicable)](https://github.com/blackbunt/rb-scrobbler)

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the tool.

## Disclaimer
This project is not affiliated with Rockbox, Last.fm, or the original developers of `rb-scrobbler`. It is an independent tool designed to enhance the user experience for Linux users managing music on Rockbox-enabled iPods.
