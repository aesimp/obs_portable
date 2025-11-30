import os
import shutil
import json
import re

import tkinter as tk
from tkinter import filedialog

# Create a hidden root window
root = tk.Tk()
root.withdraw()  # We don't need a full GUI

# Prompt the user to select a folder
PORTABLE = filedialog.askdirectory(
    title="Select the folder where you want to create the portable OBS"
)

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
# Set your desired portable OBS directory here
PORTABLE = os.path.join(PORTABLE, "obs_portable")

# The source OBS program directory
OBS_INSTALL = r"C:\Program Files\obs-studio"

# The AppData source directory
APPDATA = os.path.join(os.environ["APPDATA"], "obs-studio")

# Assets folder inside portable OBS
ASSETS_DIR = os.path.join(PORTABLE, "assets")


# ------------------------------------------------------------
# Helper Function
# ------------------------------------------------------------
def newFilename(dirname, basename, counter: int = 1):
    target_path = os.path.join(dirname, f"{str(counter)}-{basename}")
    if os.path.isfile(target_path):
        counter += 1
        target_path = newFilename(dirname, basename, counter)
    return target_path

# ------------------------------------------------------------
# STEP 1 – PREPARE PORTABLE OBS STRUCTURE
# ------------------------------------------------------------
def prepare_portable_structure():
    """
    Copy OBS program files and create the basic portable structure.
    """
    print("[1] Preparing portable OBS structure...")

    os.makedirs(PORTABLE, exist_ok=True)

    # Copy OBS installation into the portable folder
    print("    - Copying OBS installation...")
    shutil.copytree(OBS_INSTALL, PORTABLE, dirs_exist_ok=True)

    # Create /config folder
    os.makedirs(os.path.join(PORTABLE, "config"), exist_ok=True)

    # Create portable_mode.txt so OBS starts in portable mode
    flag = os.path.join(PORTABLE, "portable_mode.txt")
    if not os.path.exists(flag):
        with open(flag, "w") as f:
            f.write("Portable mode enabled.")

    print("    ✓ Portable structure ready.")


# ------------------------------------------------------------
# STEP 2 – COPY PROFILES & SCENES
# ------------------------------------------------------------
def copy_profiles_and_scenes():
    """
    Copy profiles, scenes, and ini files from %APPDATA%.
    """
    print("[2] Copying profiles, scenes and ini files...")

    basic_target = os.path.join(PORTABLE, "config", "obs-studio", "basic")
    os.makedirs(basic_target, exist_ok=True)

    # Copy "profiles"
    shutil.copytree(
        os.path.join(APPDATA, "basic", "profiles"),
        os.path.join(basic_target, "profiles"),
        dirs_exist_ok=True
    )

    # Copy "scenes"
    shutil.copytree(
        os.path.join(APPDATA, "basic", "scenes"),
        os.path.join(basic_target, "scenes"),
        dirs_exist_ok=True
    )

    # Copy global.ini and user.ini
    ini_target = os.path.join(PORTABLE, "config", "obs-studio")
    os.makedirs(ini_target, exist_ok=True)

    shutil.copy2(os.path.join(APPDATA, "global.ini"), ini_target)

    user_ini = os.path.join(APPDATA, "user.ini")
    if os.path.exists(user_ini):
        shutil.copy2(user_ini, ini_target)

    print("    ✓ Profile & scene data copied.")


# ------------------------------------------------------------
# STEP 3 – PATCH global.ini
# ------------------------------------------------------------
def fix_global_ini():
    """
    Replace the [Locations] section so OBS uses the local config folder.
    """
    print("[3] Patching global.ini...")

    ini_path = os.path.join(PORTABLE, "config", "obs-studio", "global.ini")

    with open(ini_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace everything under [Locations] with portable paths
    content = re.sub(
        r"\[Locations\][^\[]+",
        "[Locations]\nConfiguration=.\nSceneCollections=.\nProfiles=.\nPluginManagerSettings=.\n\n",
        content,
        flags=re.DOTALL
    )

    with open(ini_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("    ✓ global.ini updated.")


# ------------------------------------------------------------
# STEP 4 – JSON PARSING: PATH DETECTION
# ------------------------------------------------------------
def is_file_path(value: str) -> bool:
    """
    Check if a string looks like a file path and exists on disk.
    Only absolute Windows paths are considered.
    """
    if not isinstance(value, str):
        return False

    # Check for "C:\something..."
    if re.match(r"^[A-Za-z]:\\", value):
        return os.path.exists(value)

    # Check UNC paths \\server\...
    if value.startswith("\\\\") and os.path.exists(value) and os.path.isfile(value):
        return True

    if os.path.isfile(value):
        return True

    return False


# ------------------------------------------------------------
# STEP 5 – RECURSIVE JSON PROCESSOR
# ------------------------------------------------------------
def process_json_value(value):
    """
    Recursively walk through JSON structures.
    If a value is a file path, copy the file and replace the path.
    """
    if isinstance(value, dict):
        for key in list(value.keys()):
            value[key] = process_json_value(value[key])
        return value

    elif isinstance(value, list):
        return [process_json_value(v) for v in value]

    elif isinstance(value, str):
        if is_file_path(value):
            basename = os.path.basename(value)
            target_path = newFilename(ASSETS_DIR, basename)

            # Copy file to /assets
            os.makedirs(ASSETS_DIR, exist_ok=True)
            print(f"    Copying file: {basename}")
            shutil.copy2(value, target_path)

            basename = os.path.basename(target_path)

            # Replace with portable relative path
            return f"../../assets/{basename}"

    return value


# ------------------------------------------------------------
# STEP 6 – PROCESS ALL SCENE JSON FILES
# ------------------------------------------------------------
def process_scene_json_files():
    """
    Scan all JSON files in the scenes folder.
    Copy media files and rewrite their paths.
    """
    print("[4] Processing JSON scene files...")

    scenes_dir = os.path.join(PORTABLE, "config", "obs-studio", "basic", "scenes")

    for filename in os.listdir(scenes_dir):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(scenes_dir, filename)
        print(f"    - Processing {filename}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Recursively process
        data = process_json_value(data)

        # Save updated JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    print("    ✓ Scene files updated.")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    print("=== OBS Portable Builder (JSON parser version) ===\n")

    prepare_portable_structure()
    copy_profiles_and_scenes()
    fix_global_ini()
    process_scene_json_files()

    print("\n=== Completed successfully ===")
