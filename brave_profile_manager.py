#!/usr/bin/env python3
"""
Brave Profile Manager - A comprehensive tool to manage Brave browser profiles and launchers

This script provides functionality to:
1. List all Brave browser profiles
2. Create desktop launchers for profiles with custom titles
3. Manage (view and remove) existing profile launchers

MIT License

Copyright (c) 2025 Karsten

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import json
from pathlib import Path
import sys
import subprocess
import re

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def find_brave_profiles():
    """Find and return all Brave browser profiles with their IDs and names."""
    
    # Default Brave browser profile location
    brave_path = Path.home() / ".config" / "BraveSoftware" / "Brave-Browser"
    
    # Check if the Brave directory exists
    if not brave_path.exists():
        print(f"Brave browser profile directory not found at: {brave_path}")
        print("Please make sure Brave browser is installed and has been run at least once.")
        return []
    
    # Look for Local State file which contains profile information
    local_state_path = brave_path / "Local State"
    if not local_state_path.exists():
        print(f"Brave browser Local State file not found at: {local_state_path}")
        return []
    
    # Read and parse the Local State file
    try:
        with open(local_state_path, 'r', encoding='utf-8') as file:
            local_state = json.load(file)
    except (json.JSONDecodeError, UnicodeDecodeError, IOError) as e:
        print(f"Error reading Brave browser Local State file: {e}")
        return []
    
    # Extract profile information
    profiles = []
    if 'profile' in local_state and 'info_cache' in local_state['profile']:
        for profile_id, profile_info in local_state['profile']['info_cache'].items():
            name = profile_info.get('name', 'Unknown')
            profiles.append((profile_id, name))
    
    return profiles

def find_brave_profile_launchers():
    """Find all Brave profile desktop files in the user's applications directory."""
    
    # Only look in the user's applications directory
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    
    # Check if the directory exists
    if not desktop_dir.exists():
        print(f"Applications directory not found at: {desktop_dir}")
        return []
    
    # Look for Brave profile desktop files
    brave_desktop_files = []
    
    # Examine all desktop files
    for desktop_path in desktop_dir.glob("*.desktop"):
        filename = desktop_path.name
        
        # Check the content to see if it's a Brave profile launcher
        try:
            with open(desktop_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Check if it's a Brave-related file
                if "brave" not in content.lower():
                    continue
                
                # Check if it's a profile launcher (contains --profile-directory)
                if "--profile-directory" not in content:
                    continue
                
                # Extract profile ID from command line
                profile_id = "default"
                cmd_match = re.search(r'--profile-directory=["\']?(.*?)["\']?(\s|$)', content)
                if cmd_match:
                    profile_id = cmd_match.group(1)
                
                # Extract profile name from Name field
                profile_name = "Unknown"
                name_match = re.search(r'Name=(.*?)(\n|$)', content)
                if name_match:
                    full_name = name_match.group(1).strip()
                    if " - " in full_name and full_name.lower().startswith("brave"):
                        profile_name = full_name.split(" - ", 1)[1]
                    else:
                        profile_name = full_name
                
                # Check if it was created by our script (filename pattern)
                created_by_script = filename.startswith("brave-")
                
                brave_desktop_files.append({
                    'filename': filename,
                    'path': desktop_path,
                    'profile_name': profile_name,
                    'profile_id': profile_id,
                    'created_by_script': created_by_script,
                    'is_system': False  # Never system files since we only look at ~/.local
                })
        except Exception:
            # Skip files we can't parse correctly
            continue
    
    return brave_desktop_files

def create_desktop_file(profile_id, profile_name, custom_title=None):
    """Create a Gnome desktop file for the specified Brave profile."""
    
    # Find the path to the Brave executable
    brave_path = ""
    possible_paths = [
        "/usr/bin/brave-browser",
        "/usr/bin/brave",
        "/snap/bin/brave",
        "/opt/brave.com/brave/brave"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            brave_path = path
            break
    
    if not brave_path:
        try:
            # Try to find brave using which command
            result = subprocess.run(['which', 'brave-browser'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                brave_path = result.stdout.strip()
            else:
                result = subprocess.run(['which', 'brave'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    brave_path = result.stdout.strip()
        except Exception:
            pass
    
    if not brave_path:
        print("Error: Could not find Brave browser executable.")
        print("Please enter the path to the Brave browser executable:")
        brave_path = input("> ").strip()
        if not brave_path or not os.path.exists(brave_path):
            print("Invalid path. Desktop file not created.")
            return False
    
    # Create the desktop directory if it doesn't exist
    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a safe filename - replace spaces and slashes with underscores in both profile name and ID
    safe_name = profile_name.replace(" ", "_").replace("/", "_").lower()
    safe_id = str(profile_id).replace(" ", "_").replace("/", "_")
    desktop_filename = f"brave-{safe_name}-{safe_id}.desktop"
    desktop_path = desktop_dir / desktop_filename
    
    # Use the brave executable directly with the profile directory parameter
    exec_command = f"{brave_path} --profile-directory=\"{profile_id}\""
    
    # Use custom title if provided, otherwise use default format
    title = custom_title if custom_title else f"Brave - {profile_name}"
    
    # Create the desktop file content
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={title}
Comment=Access {profile_name} profile in Brave
Exec={exec_command}
Icon=brave-browser
Terminal=false
StartupNotify=true
Categories=Network;WebBrowser;
"""
    
    # Write the desktop file
    try:
        with open(desktop_path, 'w') as file:
            file.write(desktop_content)
        
        # Make the desktop file executable
        os.chmod(desktop_path, 0o755)
        print(f"Desktop file created: {desktop_path}")
        return True
    except Exception as e:
        print(f"Error creating desktop file: {e}")
        return False

def remove_desktop_file(desktop_file_info):
    """Remove a desktop file."""
    try:
        # Check if we can remove the file
        if desktop_file_info['is_system']:
            print(f"Warning: Cannot remove system file: {desktop_file_info['path']}")
            print("You would need sudo privileges to remove this file.")
            return False
            
        # Remove the desktop file
        desktop_file_info['path'].unlink()
        print(f"Removed desktop file: {desktop_file_info['path']}")
        return True
    except Exception as e:
        print(f"Error removing desktop file: {e}")
        return False

def wait_for_input():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to return to the main menu...")

def list_profiles():
    """List all Brave browser profiles."""
    clear_screen()
    print("=== BRAVE PROFILES ===")
    print("Listing all available Brave profiles...")
    print()
    
    profiles = find_brave_profiles()
    
    if not profiles:
        print("No Brave browser profiles found.")
        wait_for_input()
        return
    
    print("Brave Browser Profiles:")
    print("----------------------")
    for idx, (profile_id, name) in enumerate(profiles, 1):
        print(f"{idx}. ID: {profile_id}")
        print(f"   Name: {name}")
        print()
    
    wait_for_input()

def create_launcher():
    """Create desktop launchers for Brave profiles."""
    clear_screen()
    print("=== CREATE PROFILE LAUNCHER ===")
    print("Create desktop launchers for Brave profiles")
    print()
    
    profiles = find_brave_profiles()
    
    if not profiles:
        print("No Brave browser profiles found.")
        wait_for_input()
        return
    
    print("\nAvailable Brave Browser Profiles:")
    print("--------------------------------")
    for idx, (profile_id, name) in enumerate(profiles, 1):
        print(f"{idx}. {name} (ID: {profile_id})")
    
    print("\nSelect a profile to create a desktop shortcut (enter number), or 'a' for all profiles:")
    choice = input("> ").strip()
    
    if choice.lower() == 'a':
        # Ask if user wants custom titles
        use_custom_titles = input("\nDo you want to customize launcher titles? (y/n): ").strip().lower() == 'y'
        
        # Create desktop files for all profiles
        for profile_id, name in profiles:
            custom_title = None
            if use_custom_titles:
                print(f"\nEnter custom title for '{name}' profile (or leave empty for default 'Brave - {name}'):")
                custom_title = input("> ").strip()
                if not custom_title:
                    custom_title = None  # Use default if empty
            
            create_desktop_file(profile_id, name, custom_title)
            
        print("\nDesktop shortcuts created for all profiles.")
        print("You may need to restart the shell or log out and back in for them to appear in the application menu.")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                profile_id, name = profiles[idx]
                
                # Ask for custom title
                print(f"\nEnter custom title for the launcher (or leave empty for default 'Brave - {name}'):")
                custom_title = input("> ").strip()
                if not custom_title:
                    custom_title = None  # Use default if empty
                
                if create_desktop_file(profile_id, name, custom_title):
                    print(f"\nDesktop shortcut created for '{name}' profile.")
                    print("You may need to restart the shell or log out and back in for it to appear in the application menu.")
            else:
                print("Invalid selection. No desktop file created.")
        except ValueError:
            print("Invalid input. Please enter a number or 'a'.")
    
    wait_for_input()

def manage_launchers():
    """Manage existing profile launchers."""
    clear_screen()
    print("=== MANAGE PROFILE LAUNCHERS ===")
    print("Manage existing Brave profile launchers")
    print()
    
    desktop_files = find_brave_profile_launchers()
    
    if not desktop_files:
        print("No Brave profile launchers found.")
        wait_for_input()
        return
    
    print("Installed Brave Profile Launchers:")
    print("--------------------------------")
    for idx, file_info in enumerate(desktop_files, 1):
        print(f"{idx}. {file_info['profile_name']} (ID: {file_info['profile_id']})")
        print(f"   File: {file_info['path']}")
        print()
    
    print("Options:")
    print("  1. Remove a specific profile launcher")
    print("  2. Remove all profile launchers created by this script")
    print("  3. Return to main menu")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        profile_idx = input("\nEnter the number of the profile launcher to remove: ").strip()
        try:
            idx = int(profile_idx) - 1
            if 0 <= idx < len(desktop_files):
                file_info = desktop_files[idx]
                if file_info['is_system']:
                    print("\nThis is a system-wide launcher and requires sudo privileges to remove.")
                    print("You can manually remove it with:")
                    print(f"  sudo rm '{file_info['path']}'")
                else:
                    if remove_desktop_file(file_info):
                        print(f"\nSuccessfully removed launcher for '{file_info['profile_name']}' profile.")
            else:
                print("Invalid selection. No changes made.")
        except ValueError:
            print("Invalid input. No changes made.")
    
    elif choice == '2':
        confirm = input("\nAre you sure you want to remove ALL Brave profile launchers created by this script? (y/n): ").strip().lower()
        if confirm == 'y':
            removed_count = 0
            script_created_files = [f for f in desktop_files if f['created_by_script'] and not f['is_system']]
            
            if not script_created_files:
                print("No launchers created by this script were found.")
                wait_for_input()
                return
                
            for file_info in script_created_files:
                if remove_desktop_file(file_info):
                    removed_count += 1
            print(f"\nRemoved {removed_count} of {len(script_created_files)} Brave profile launchers.")
        else:
            print("Operation cancelled. No changes made.")
    
    elif choice == '3':
        # Return directly to main menu without waiting for input
        return
    
    wait_for_input()

def display_main_menu():
    """Display the main menu and handle user input."""
    while True:
        clear_screen()
        print("=== BRAVE PROFILE MANAGER ===")
        print("1. Manage Profile Launchers")
        print("2. Create Profile Launcher")
        print("3. List Brave Profiles")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            manage_launchers()
        elif choice == "2":
            create_launcher()
        elif choice == "3":
            list_profiles()
        elif choice == "4":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid option. Please choose 1-4.")
            wait_for_input()

if __name__ == "__main__":
    display_main_menu()