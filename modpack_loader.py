"""modpack_loader.py

Loader for a local Minecraft modpack directory or zip for use by the custom launcher.

Public API:
  load_modpack(path) -> dict

Only uses stdlib: os, shutil, zipfile, pathlib
"""
import os
import shutil
import zipfile
from pathlib import Path


def _unpack_zip(src_zip: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src_zip, 'r') as z:
        z.extractall(dest_dir)
    return dest_dir


def _is_zip(path: Path) -> bool:
    return zipfile.is_zipfile(path)


def load_modpack(path):
    """Load a modpack from a directory or ZIP file.

    Args:
        path (str or Path): path to a modpack folder or a .zip file

    Returns:
        dict: information about the unpacked/loaded modpack (see spec)

    Raises:
        Exception: if mandatory `mods/` folder is missing or contains no .jar files
    """
    p = Path(path)

    # If zip -> unpack into profiles/<name>
    if p.is_file() and _is_zip(p):
        name = p.stem
        dest = Path('profiles') / name
        _unpack_zip(p, dest)
        base = dest
    elif p.is_dir():
        base = p
    else:
        raise Exception(f"Modpack path not found: {path}")

    mods_dir = base / 'mods'
    if not mods_dir.exists():
        raise Exception('Modpack missing mods folder')

    # Find jar files
    jars = [f for f in mods_dir.iterdir() if f.is_file() and f.suffix.lower() == '.jar']
    if not jars:
        raise Exception('Modpack contains no mods')

    info = {
        'gameDir': str(base.resolve()),
        'modsDir': str(mods_dir.resolve()),
        'assetsDir': str(Path('./1.8.9_assets').resolve()),
        'version': 'MozClient',
        'tweakClass': 'net.minecraftforge.fml.common.launcher.FMLTweaker'
    }

    # Optional entries
    for opt in ('resourcepacks', 'shaderpacks'):
        pth = base / opt
        if pth.exists():
            info[f'{opt}Dir'] = str(pth.resolve())

    for opt in ('options.txt', 'optionsof.txt'):
        pth = base / opt
        if pth.exists():
            info[opt.replace('.', '')] = str(pth.resolve())

    return info


if __name__ == '__main__':
    # quick smoke test when run directly
    import sys
    if len(sys.argv) < 2:
        print('Usage: python modpack_loader.py <modpack-path>')
        raise SystemExit(1)
    print(load_modpack(sys.argv[1]))
