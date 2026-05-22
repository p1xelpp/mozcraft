import json
import os
import sys
import subprocess

from vulkanpatch import apply_vulkan_patch
from offlinepatch import apply_offline_patch
from argpatch import substitute_args
from offlinehash import get_username
from onlineauth import apply_online_auth, clear_auth_cache

from legacy_mode import is_legacy_version
from legacy_java import select_legacy_java
from legacy_jvm_patch import apply_legacy_jvm_args
from legacy_natives import apply_legacy_natives

from modern_java import select_modern_java  

from gamedir import get_game_directory   # ← NEW
from assetsdir import get_assets_directory
from modpack_loader import load_modpack

mc = os.path.join(os.getenv("APPDATA"), ".minecraft")

# Check for --legacy argument
force_legacy = "--legacy" in sys.argv

# Which version do you want to start? (with --modpack: first modpack path/name)
version = None
if '--modpack' in sys.argv or '--importmodpack' in sys.argv:
    mp_input = input("Enter modpack filename (in project root or modpacks/) or press Enter to use ModpackBuild: ")
    mp_path = None
    if mp_input:
        # check project root and modpacks/
        cand = os.path.abspath(mp_input)
        if os.path.exists(cand):
            mp_path = cand
        else:
            cand2 = os.path.abspath(os.path.join('modpacks', mp_input))
            if os.path.exists(cand2):
                mp_path = cand2
    else:
        cand = os.path.abspath('ModpackBuild')
        if os.path.exists(cand):
            mp_path = cand

    if mp_path:
        try:
            modpack_info = load_modpack(mp_path)
            print('Loaded modpack from', mp_path)
            modpack_source_path = mp_path
            game_directory = modpack_info['gameDir']
            # override values now; assets root may be present
            # set a sensible default minecraft version from manifest if present
            manifest_path = os.path.join(mp_path, 'manifest.json')
            default_version = None
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as mf:
                        mfj = json.load(mf)
                        default_version = mfj.get('minecraftVersion')
                except:
                    default_version = None
            # don't touch `values` here (not created yet) — store temp overrides
            modpack_game_directory = game_directory
            modpack_assets_root = modpack_info.get('assetsDir')
            if default_version:
                ask = input(f"Enter Minecraft version to launch [{default_version}]: ")
                version = ask.strip() or default_version
        except Exception as e:
            print('ERROR: failed to load modpack:', e)
            exit(1)
    else:
        print('No modpack found; continuing to normal version prompt.')

if not version:
    version = input("Enter Minecraft version to launch: ")

# Paths to JSON and JAR
json_path = os.path.join(mc, "versions", version, f"{version}.json")
jar_path = os.path.join(mc, "versions", version, f"{version}.jar")

# Load JSON
try:
    with open(json_path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    # Try to find a matching installed version case-insensitively or by prefix
    versions_dir = os.path.join(os.getenv('APPDATA'), '.minecraft', 'versions')
    matched_json = None
    matched_version = None
    if os.path.isdir(versions_dir):
        for entry in os.listdir(versions_dir):
            if entry.lower() == version.lower() or entry.lower().startswith(version.lower()):
                candidate = os.path.join(versions_dir, entry, f"{entry}.json")
                if os.path.exists(candidate):
                    matched_json = candidate
                    matched_version = entry
                    break
    if matched_json:
        print(f"Using installed version: {matched_version}")
        json_path = matched_json
        with open(json_path, "r") as f:
            data = json.load(f)
        version = matched_version
        jar_path = os.path.join(mc, "versions", version, f"{version}.jar")
    else:
        # If we loaded a modpack from project, try to find the version JSON inside it
        if 'modpack_source_path' in globals():
            mp = modpack_source_path
            # If modpack is a directory, check for versions/<version>/<version>.json
            if os.path.isdir(mp):
                candidate = os.path.join(mp, 'versions', version, f"{version}.json")
                if os.path.exists(candidate):
                    print(f"Using version JSON from modpack: {candidate}")
                    json_path = candidate
                    with open(json_path, "r") as f:
                        data = json.load(f)
                    jar_path = os.path.join(mp, 'versions', version, f"{version}.jar")
                else:
                    print(f"File not found: {json_path}")
                    exit(1)
            else:
                print(f"File not found: {json_path}")
                exit(1)
        else:
            print(f"File not found: {json_path}")
            exit(1)

# Load base data if Forge (inheritsFrom)
base_data = None
if "inheritsFrom" in data:
    base_version = data["inheritsFrom"]
    base_json_path = os.path.join(mc, "versions", base_version, f"{base_version}.json")
    try:
        with open(base_json_path, "r") as f:
            base_data = json.load(f)
    except:
        print("ERROR: Forge base version JSON niet gevonden:", base_json_path)
        exit(1)

# Main class from JSON
main_class = data["mainClass"]

# Collect all libraries (Forge + base)
libraries = []

# Load libraries from Forge version
for lib in data["libraries"]:
    # Forge: legacy format (no downloads/artifact)
    if "name" in lib and "downloads" not in lib:
        group, artifact, lib_version = lib["name"].split(":")
        path = os.path.join(
            mc,
            "libraries",
            group.replace(".", "/"),
            artifact,
            lib_version,
            f"{artifact}-{lib_version}.jar"
        )
        libraries.append(path)
    # Modern/vanilla format with downloads.artifact
    elif "downloads" in lib and "artifact" in lib["downloads"]:
        path = lib["downloads"]["artifact"]["path"]
        libraries.append(os.path.join(mc, "libraries", path))

# Load libraries from base version (Vanilla format)
if base_data:
    for lib in base_data["libraries"]:
        if "downloads" in lib and "artifact" in lib["downloads"]:
            path = lib["downloads"]["artifact"]["path"]
            libraries.append(os.path.join(mc, "libraries", path))

# Filter duplicates and bad LWJGL versions
libraries = list(dict.fromkeys(libraries))  # Remove duplicates
libraries = [
    lib for lib in libraries
    if "2.9.2-nightly-20140822" not in lib
]

# Build classpath
classpath = os.pathsep.join(libraries + [jar_path])

# JVM args from JSON (strings only)
if "arguments" in data:
    jvm_args = [arg for arg in data["arguments"]["jvm"] if isinstance(arg, str)]
    game_args = [arg for arg in data["arguments"]["game"] if isinstance(arg, str)]
elif base_data and "arguments" in base_data:
    # Forge inherits from base version
    jvm_args = [arg for arg in base_data["arguments"]["jvm"] if isinstance(arg, str)]
    game_args = [arg for arg in base_data["arguments"]["game"] if isinstance(arg, str)]
elif "minecraftArguments" in data:
    # Legacy format in direct data
    jvm_args = []
    game_args = data["minecraftArguments"].split()
elif base_data and "minecraftArguments" in base_data:
    # Legacy format in base data (Forge 1.8.9)
    jvm_args = []
    game_args = base_data["minecraftArguments"].split()
else:
    print("ERROR: Could not find arguments in JSON")
    exit(1)

# Check for --online mode
online_mode = "--online" in sys.argv
logout_only = "--logout" in sys.argv

# Handle logout and exit
if logout_only:
    clear_auth_cache()
    print("Logged out successfully")
    exit(0)

# Apply authentication based on mode
if online_mode:
    print("Online mode enabled - attempting to authenticate...")
    # Don't apply offline patch in online mode
else:
    print("Offline mode enabled")
    # Apply offline patch for offline mode
    jvm_args = apply_offline_patch(jvm_args)

# -------------------------------
#   GAME DIRECTORY PER VERSION
# -------------------------------
game_directory = get_game_directory(version)

# -------------------------------
#   ASSET INDEX FIX (Forge support)
# -------------------------------
if "assetIndex" in data:
    # Vanilla or modern versions
    asset_index = data["assetIndex"]["id"]
elif base_data and "assetIndex" in base_data:
    # Forge inherits from base version
    asset_index = base_data["assetIndex"]["id"]
else:
    print("ERROR: No assetIndex found in this version.")
    exit(1)

# -------------------------------
#   VALUES FOR ARGPATCH
# -------------------------------
values = {
    "auth_player_name": get_username(),
    "auth_uuid": "00000000-0000-0000-0000-000000000000",
    "auth_access_token": "0",
    "assets_root": get_assets_directory(version),
    "assets_index_name": asset_index,
    "game_directory": game_directory,
    "classpath": classpath,
    "launcher_name": "MozCraft",
    "launcher_version": "1.0",
    "version_name": version,
    "user_properties": "{}",
    "user_type": "legacy"
}

# If we loaded a modpack earlier, update values accordingly
if 'modpack_game_directory' in globals():
    values['game_directory'] = modpack_game_directory
if 'modpack_assets_root' in globals() and modpack_assets_root:
    values['assets_root'] = modpack_assets_root

# Handle online mode authentication
if online_mode:
    print("\nStarting Microsoft authentication flow...")
    auth_values = apply_online_auth(values, use_cache=True)
    if auth_values is None:
        print("ERROR: Authentication failed. Cannot launch in online mode.")
        exit(1)
    values = auth_values
    # Remove offline flags since we're using real authentication
    jvm_args = [arg for arg in jvm_args if "minecraft.server.online-mode=false" not in arg]

# Apply argpatch
jvm_args = substitute_args(jvm_args, values)
game_args = substitute_args(game_args, values)

# Replace hardcoded assets directory with dynamic one
for i, arg in enumerate(game_args):
    if arg == "--assetsDir" and i + 1 < len(game_args):
        game_args[i + 1] = get_assets_directory(version)

script_dir = os.path.dirname(__file__)
natives_folder = os.path.join(script_dir, "natives")

# -------------------------------
#        LEGACY MODE CHECK
# -------------------------------
# Load modpack when requested via CLI flag --modpack or --importmodpack
modpack_info = None
if '--modpack' in sys.argv or '--importmodpack' in sys.argv:
    modpack_path = os.path.abspath('ModpackBuild')
    if not os.path.exists(modpack_path):
        print('ERROR: ModpackBuild folder not found at', modpack_path)
        exit(1)
    try:
        modpack_info = load_modpack(modpack_path)
        print('Loaded modpack from', modpack_path)
        # override game directory and assets (apply to variables; values updated later)
        modpack_source_path = modpack_path
        game_directory = modpack_info['gameDir']
        modpack_assets_root = modpack_info.get('assetsDir')
    except Exception as e:
        print('ERROR: failed to load ModpackBuild:', e)
        exit(1)

if force_legacy or is_legacy_version(version):
    print("Legacy mode enabled for", version)

    java_path = select_legacy_java()
    lwjgl_native_path = natives_folder

    # Legacy JVM patches
    jvm_args = apply_legacy_jvm_args(jvm_args, lwjgl_native_path)
    apply_legacy_natives(lwjgl_native_path, "patched_lwjgl2")

    # LWJGL2 native path
    jvm_args.insert(0, f"-Dorg.lwjgl.librarypath={lwjgl_native_path}")

    # HARD CLEANUP: NO MODERN FLAGS IN LEGACY
    jvm_args = [a for a in jvm_args if "--add-opens" not in a]

else:
    print("Modern mode enabled")
    java_path = select_modern_java(version)

# -------------------------------
#        BUILD COMMAND
# -------------------------------
cmd = [java_path, "-Xmx2G"] + jvm_args + ["-cp", classpath, main_class] + game_args

print("mc launch command:", " ".join(cmd))
print("Launching Minecraft…")
subprocess.run(cmd)
