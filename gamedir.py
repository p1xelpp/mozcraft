import os

def get_game_directory(version: str) -> str:
    """
    Returns a unique game directory per version.
    Example:
        1.8.9  → mozcraft/1.8.9
        1.20.6 → mozcraft/1.20.6
        1.8.9-forge... → mozcraft/1.8.9 (base version)
    """

    # Extract base version for Forge
    base_version = version.split("-")[0] if "-" in version else version

    base = os.path.dirname(__file__)  # directory where main.py is located
    version_dir = os.path.join(base, base_version)

    # Create the directory if it doesn't exist yet
    if not os.path.exists(version_dir):
        os.makedirs(version_dir)

    return version_dir
