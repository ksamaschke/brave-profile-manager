# Brave Profile Manager

A comprehensive tool for managing Brave browser profiles and creating desktop launchers for each profile.

## Features

- List all Brave browser profiles with their IDs and names
- Create desktop shortcuts for individual profiles or all profiles at once
- Add custom titles to desktop shortcuts
- Focus existing windows when launching a profile that's already open (when wmctrl is installed)
- Manage (view and remove) existing profile launchers

## Requirements

- Linux operating system with a desktop environment (tested on GNOME)
- Python 3.6 or higher
- Brave browser installed and run at least once
- `wmctrl` package (optional but recommended for window focusing functionality)

## Installation

1. Clone this repository or download the files:
   ```
   git clone https://github.com/yourusername/brave-profile-manager.git
   cd brave-profile-manager
   ```

2. Make the main script executable:
   ```
   chmod +x brave_profile_manager.py
   ```

3. Install the optional dependency for window focusing (recommended):
   ```
   # Ubuntu/Debian
   sudo apt-get install wmctrl
   
   # Fedora
   sudo dnf install wmctrl
   
   # Arch Linux
   sudo pacman -S wmctrl
   
   # openSUSE
   sudo zypper install wmctrl
   ```
   Note: Without wmctrl, the script will still create launchers but they won't be able to focus existing windows.

## Usage

Run the main script:
```
./brave_profile_manager.py
```

The script presents a menu with the following options:
1. **List Brave Profiles** - Shows all available Brave profiles
2. **Create Profile Launcher** - Creates desktop shortcuts for selected profiles
3. **Manage Profile Launchers** - Lists and allows removal of existing launchers
4. **Exit** - Exits the program

### Creating Profile Launchers

When creating profile launchers, you can:
- Create a launcher for a specific profile
- Create launchers for all profiles at once
- Add custom titles to the launchers

The launchers will be created in your `~/.local/share/applications/` directory and will appear in your application menu.

### Managing Profile Launchers

The management option allows you to:
- View all installed Brave profile launchers
- Remove a specific launcher
- Remove all launchers created by this script

## How It Works

The script works by:
1. Reading Brave's `Local State` file to identify available profiles
2. Creating desktop files (.desktop) in the standard Linux applications directory
3. Creating a single generic helper script in `~/.local/bin/` to handle window focusing
4. Using wmctrl (if installed) to focus existing windows instead of launching new ones

### Generic Helper Script for Window Focusing

The script creates a single generic helper script (`brave-profile-launcher.sh`) in `~/.local/bin/` that:

- Takes two parameters: `<profile_id>` and optionally `<profile_name>`
- Checks if a Brave window with the specified profile is already running
- Focuses the existing window if found (including windows on other virtual desktops)
- Launches a new instance of the profile if no existing window is found

This approach:
- Minimizes file system clutter by using a single script for all profiles
- Makes the script parameters easily identifiable in desktop files
- Enables robust window detection across virtual desktops based on process IDs

### Note on Virtual Desktops and Window Focusing

The window focusing feature attempts to find and focus Brave windows across different virtual desktops, but its effectiveness may vary based on:

- Your desktop environment (GNOME, KDE, etc.)
- How Brave manages its windows and processes
- Window state (minimized, on different workspaces)

The script employs multiple window-finding techniques, but there may be cases where a new window is opened instead of focusing an existing one. This is a limitation of how window managers and browsers interact rather than a bug in the script.

## License

This project is licensed under the MIT License - see the LICENSE file for details.