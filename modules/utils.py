import subprocess
from pathlib import Path
from InquirerPy import inquirer

def get_music_folder() -> str:
    """Get the music folder dynamically using xdg-user-dir."""
    result = subprocess.run(["xdg-user-dir", "MUSIC"], capture_output=True, text=True)
    music_dir = result.stdout.strip()

    # Fallback to ~/Musik if xdg-user-dir fails
    if not music_dir or not Path(music_dir).is_dir():
        music_dir = str(Path.home() / "Music")  # Default for English systems

    return music_dir

def get_device_for_mountpoint(mountpoint: str) -> str:
    """
    Determines the device associated with a given mountpoint.
    Returns the device identifier (e.g., /dev/sdb2).
    """
    try:
        # Run lsblk with the specified column options
        result = subprocess.run(
            ['lsblk', '-o', 'NAME,MOUNTPOINT', '--noheadings', '--raw'],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the output
        for line in result.stdout.splitlines():
            #print(f"Line: {line}")
            columns = line.split(None, 1)  # Split into NAME and MOUNTPOINT
            #print(f"Columns: {columns}")
            if len(columns) == 2:
                device, mount = columns
                # Decode \\x20 to a regular space
                normalized_mount = mount.encode('utf-8').decode('unicode_escape').strip()
                # Convert PosixPath to string
                if normalized_mount == str(mountpoint).strip():
                    #print(f"Found device: /dev/{device}")
                    return f"/dev/{device}"

        # Raise an exception if no device is found
        raise FileNotFoundError(f"No device found for mountpoint {mountpoint}.")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running lsblk: {e.stderr}")
    
def list_blocking_processes(mountpoint: str):
    """
    Lists processes using the given device or mountpoint.
    Returns a list of strings containing information about the blocking processes.
    """
    try:
        result = subprocess.run(
            ['lsof', mountpoint],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:  # No error, just no processes found
            return []
        raise RuntimeError(f"Error running lsof: {e.stderr}")

def safely_unmount_ipod(mountpoint: str):
    """
    Safely unmounts the iPod and powers it off.
    Notifies the user about blocking processes.
    """
    try:
        # Determine the device for the mountpoint
        device = get_device_for_mountpoint(mountpoint)

        # Check if any processes are using the device
        blocking_processes = list_blocking_processes(mountpoint)
        if blocking_processes:
            print(f"The device {device} is currently being used by the following processes:")
            for process in blocking_processes:
                print(process)

            # User confirmation with InquirerPy
            confirm = inquirer.confirm(
                message="Do you want to unmount the device anyway?",
                default=False
            ).execute()

            if not confirm:
                print("Unmounting canceled.")
                return

        # Unmount the device
        subprocess.run(['udisksctl', 'unmount', '-b', device], check=True)
        print(f"iPod {device} was successfully unmounted.")

        # Power off the device
        subprocess.run(['udisksctl', 'power-off', '-b', device], check=True)
        print(f"iPod {device} was safely removed.")
        exit(0)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error safely removing the iPod: {e}")
