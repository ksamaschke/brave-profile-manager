# Brave Profile Manager

Managing Brave Profiles together with .desktop Files on Linux sucks, as Brave does not use the names of the profiles in any file-names or other easily identifyable means. So if one wanted to create a dedicated .desktop-File to launch into a certain Brave Profile, this simply would not work, unless I did a lot of research.

Or unless I used this script.

## Features

- List all Brave browser profiles with their IDs and names
- Create desktop shortcuts for individual profiles or all profiles at once
- Add custom titles to desktop shortcuts
- Manage (view and remove) existing profile launchers

## Requirements

- Linux operating system with a desktop environment (tested on GNOME)
- Python 3.6 or higher
- Brave browser installed and run at least once

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

## Usage

Run the main script:
```
./brave_profile_manager.py
```

The script presents a menu with the following options:
1. **Manage Profile Launchers** - Lists and allows removal of existing launchers
2. **Create Profile Launcher** - Creates desktop shortcuts for selected profiles
3. **List Brave Profiles** - Shows all available Brave profiles
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
3. Each desktop file directly launches Brave with the appropriate profile parameter

## License

This project is licensed under the MIT License - see the LICENSE file for details.