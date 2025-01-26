#!/bin/bash

# Get the music folder dynamically using xdg-user-dir
get_music_folder() {
    local music_dir
    music_dir=$(xdg-user-dir MUSIC)

    # Fallback to ~/Musik if xdg-user-dir fails
    if [[ -z $music_dir || ! -d $music_dir ]]; then
        music_dir="${HOME}/Musik"  # Use "Musik" as default for German systems
    fi

    echo "$music_dir"
}

# Find connected iPods
find_ipods() {
    local ipods=()
    for mount in /run/media/$USER/*; do
        if [[ -d "$mount/iPod_Control" ]]; then
            ipods+=("$mount")
        fi
    done
    printf "%s\n" "${ipods[@]}"
}

# Prompt user to select an iPod
select_ipod() {
    local ipods
    ipods=$(find_ipods)
    if [[ -z $ipods ]]; then
        gum style --foreground 196 "No iPod found. Please ensure your iPod is connected."
        exit 1
    fi
    echo "$ipods" | gum choose
}

# List artists (top-level directories) in a given directory
list_artists() {
    local dir="$1"
    local artists
    artists=$(find "$dir" -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 -n 1 basename | sort)
    echo $artists
}

# Prompt user to select one or more artists
select_artists() {
    local dir="$1"
    local $artists
    # Direkt die Liste an gum übergeben
    artists=$(list_artists "$dir" | gum choose --no-limit)
    echo $artists
}
# Perform file operations (copy or delete)
perform_file_operation() {
    local source="$1"
    local target="$2"
    local mode="$3" # copy or delete
    # Check if the source directory exists
    if [[ ! -d "$source" ]]; then
        gum style --foreground 196 "Source directory '$source' does not exist. Operation aborted."
        exit 1
    fi
    
    file_types=(".mp3" ".flac" ".m4a")
    rsync_options="-avh --progress --include='*/'"

    # Add file type filters
    for ext in "${file_types[@]}"; do
        rsync_options="$rsync_options --include='*${ext}'"
    done
    rsync_options="$rsync_options --exclude='*'"

    case $mode in
        "copy")
            echo "Starting file transfer..."
            rsync $rsync_options "$source/" "$target/"
            ;;
        "delete")
            echo "Deleting files..."
            rm -rf "$source"
            ;;
    esac

    if [[ $? -eq 0 ]]; then
        gum style --foreground 46 "Operation successful!"
    else
        gum style --foreground 196 "An error occurred!"
    fi
}

# Copy music to iPod
copy_music() {
    local source_dir="$1"
    local selected_artists
    local selected_ipod
    local target_dir

    selected_artists=$(select_artists "$source_dir")
    if [[ -z $selected_artists ]]; then
        gum style --foreground 196 "No artists selected. Exiting."
        exit 1
    fi
    
    selected_ipod=$(select_ipod)
    if [[ -z $selected_ipod ]]; then
        gum style --foreground 196 "No iPod selected. Exiting."
        exit 1
    fi

    for artist in $selected_artists; do
        target_dir="$selected_ipod/Music/$artist"
        perform_file_operation "$source_dir/$artist" "$target_dir" "copy"
    done
}

# Delete music by artist from iPod
delete_music() {
    local selected_ipod
    local target_dir
    local selected_artists

    selected_ipod=$(select_ipod)
    if [[ -z $selected_ipod ]]; then
        gum style --foreground 196 "No iPod selected. Exiting."
        exit 1
    fi

    target_dir="$selected_ipod/Music"

    selected_artists=$(select_artists "$target_dir")
    if [[ -z $selected_artists ]]; then
        gum style --foreground 196 "No artists selected. Exiting."
        exit 1
    fi

    gum confirm "Are you sure you want to delete the selected artist(s) from the iPod?" || {
        gum style --foreground 226 "Deletion cancelled."
        exit 1
    }

    for artist in $selected_artists; do
        echo "Deleting artist: $artist"
        perform_file_operation "$target_dir/$artist" "" "delete"
    done
}

# Main menu
main() {
    local source_dir
    source_dir=$(get_music_folder)

    echo "Source directory is set to: $source_dir"

    action=$(gum choose "Copy music to iPod" "Delete music from iPod")
    case $action in
        "Copy music to iPod")
            copy_music "$source_dir"
            ;;
        "Delete music from iPod")
            delete_music
            ;;
        *)
            echo "Invalid selection. Exiting."
            exit 1
            ;;
    esac
}

main
