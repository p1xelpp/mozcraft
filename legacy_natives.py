import shutil
import os

def apply_legacy_natives(natives_path, patched_natives_dir):
    for file in os.listdir(patched_natives_dir):
        src = os.path.join(patched_natives_dir, file)
        dst = os.path.join(natives_path, file)
        shutil.copy(src, dst)
