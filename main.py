import json
import os
import subprocess
from vulkanpatch import apply_vulkan_patch
from offlinepatch import apply_offline_patch
from argpatch import substitute_args
from offlinehash import get_username


# Path to .minecraft
mc = os.path.join(os.getenv("APPDATA"), ".minecraft")

# Which version do you want to launch
version = "26.1.2"

# Paths to JSON and JAR
json_path = os.path.join(mc, "versions", version, f"{version}.json")
jar_path = os.path.join(mc, "versions", version, f"{version}.jar")

# JSON loading
with open(json_path, "r") as f:
    data = json.load(f)

# main class outta JSON
main_class = data["mainClass"]

# Collect all libraries
libraries = []
for lib in data["libraries"]:
    if "downloads" in lib and "artifact" in lib["downloads"]:
        path = lib["downloads"]["artifact"]["path"]
        libraries.append(os.path.join(mc, "libraries", path))

# Classpath bob building lol
classpath = os.pathsep.join(libraries + [jar_path])

jvm_args = [arg for arg in data["arguments"]["jvm"] if isinstance(arg, str)]

# Apply Vulkan patch
jvm_args = apply_vulkan_patch(jvm_args)

# Apply offline patch
jvm_args = apply_offline_patch(jvm_args)

game_args = [arg for arg in data["arguments"]["game"] if isinstance(arg, str)]


#for argpatch
values = {
    "auth_player_name": get_username(),
    "auth_uuid": "00000000-0000-0000-0000-000000000000",
    "auth_access_token": "0",
    "assets_root": os.path.join(mc, "assets"),
    "assets_index_name": data["assetIndex"]["id"],
    "game_directory": os.getcwd(),
    "classpath": classpath,
    "launcher_name": "MozCraft",
    "launcher_version": "1.0"
}

jvm_args = substitute_args(jvm_args, values)
game_args = substitute_args(game_args, values)


# bob the builder of the command
cmd = ["java", "-Xmx2G", "-cp", classpath, main_class] + jvm_args + game_args

# wahoo finally whe are usin subproccess :D
print("Launching Minecraft…")
subprocess.run(cmd)
