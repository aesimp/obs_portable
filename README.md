# Create a Portable OBS from an Existing Installation

This guide will help you create a **backup & portable version** of your existing *OBS installation*.  
There is also a compiled `.exe` available that performs all these steps automatically.

> **Nothing will be deleted or modified in your current installation!**

## Portable Folder

1. Create a folder at any location  
> `Example: F:\obs`

2. Copy the contents of `C:\Program Files\obs-studio` into the new folder `F:\obs`

3. Create the folder `config` inside `F:\obs`

4. Create the file `portable_mode.txt` inside `F:\obs`

#### (Optional)
6. Create a shortcut to the file `F:\obs\bin\64bit\obs64.exe`

7. Move the created shortcut to `F:\obs`

8. Rename the shortcut as you like  
> `Example: F:\obs\obs_portable.exe`

---

## Copy Scenes and Profiles

1. Create the folder `F:\obs\config\obs-studio\basic`

2. Copy the ***folder*** `%APPDATA%\obs-studio\basic\profiles` to `F:\obs\config\obs-studio\basic`

3. Copy the ***folder*** `%APPDATA%\obs-studio\basic\scenes` to `F:\obs\config\obs-studio\basic`

4. Copy the file `%APPDATA%\obs-studio\global.ini` to `F:\obs\config\obs-studio`

5. Copy the file `%APPDATA%\obs-studio\user.ini` to `F:\obs\config\obs-studio`

6. Replace all `[Locations]` entries in `F:\obs\config\obs-studio\global.ini` with `.`
```
[Locations]
Configuration=.
SceneCollections=.
Profiles=.
PluginManagerSettings=.
```

---

## Copy Media Files (Images/Logos/Sounds)

1. Create the folder `F:\obs\assets`

2. Search for all file paths in `F:\obs\config\obs-studio\basic\scenes\*.json`

3. Copy the files to `F:\obs\assets` and modify the paths in the JSON files to  
> `Example: ../../basename.jpg`


---

by aesimp
