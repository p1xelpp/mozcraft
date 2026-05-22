# MozCraft Launcher

A custom Minecraft launcher with offline and online mode support.

(_u have to download the source files to .minecraft, every version jar and json_ D:)
## Installation

1. Extract all files from this zip to a folder
2. Install Python 3.11+ if you haven't already
3. Install dependencies:
   ```
   pip install requests
   ```

## Usage

### Offline Mode (Default)
```
python main.py
```
Then enter the Minecraft version you want to play (e.g., `1.21.4` or `1.8.9`)

### Online Mode (Microsoft Account)
```
python main.py --online
```
You'll be prompted to log in with your Microsoft account using OAuth2.

### Logout
```
python main.py --logout
```
Clears cached authentication token.

### Legacy Mode (Force Java 8)
```
python main.py --legacy
```

### Modpack Mode
```
python main.py --modpack
```

## Features

- Offline mode (no Microsoft account required)
- Online mode with Microsoft OAuth2 authentication
- Automatic Java detection (Java 8 for legacy, Java 17+ for modern)
- Support for Forge and Fabric modded versions
- Per-version game directories (separate saves, configs, etc.)
- Per-version assets directories (legacy versions only)
- Modpack support
- Vulkan GPU support (`vulkanpatch.py`)

## Requirements

- Python 3.11+
- Java 8 (for Minecraft 1.8.9 and earlier)
- Java 17+ (for Minecraft 1.13 and later)
- `requests` library (for online auth)

## Files Included

- `main.py` - Launcher entrypoint
- `onlineauth.py` - Microsoft OAuth2 authentication
- `offlinepatch.py` - Offline mode JVM flags
- `argpatch.py` - JVM/game argument substitution
- `offlinehash.py` - Offline username generation
- `gamedir.py` - Per-version game directory handling
- `assetsdir.py` - Per-version assets directory handling
- `modpack_loader.py` - Modpack loading support
- `vulkanpatch.py` - Vulkan GPU support
- `legacy_*.py` - Legacy version support files

## Troubleshooting

### ModuleNotFoundError: requests
```
pip install requests
```

### Java not found
Make sure Java is installed and added to your system PATH.

### Minecraft won't start
Check that `.minecraft/versions/<version>/<version>.json` exists in your Appdata folder.

## License

Custom launcher for personal use.
