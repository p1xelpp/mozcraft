import os

def get_assets_directory(version: str) -> str:
    """
    Returns a unique assets directory per version.
    Example:
        1.8.9  → mozcraft/1.8.9_assets
        1.20.6 → .minecraft/assets (modern)
        1.8.9-forge... → mozcraft/1.8.9_assets (base version)
    """

    # Extract base version for Forge
    base_version = version.split("-")[0] if "-" in version else version

    # Modern versions use global assets
    # (everything from 1.13, or version 2+)
    def is_modern(v):
        try:
            parts = v.split(".")
            major = int(parts[0])
            if major >= 2:
                return True  # 2.x, 3.x, etc. are modern
            if major == 1:
                minor = int(parts[1])
                return minor >= 13  # 1.13+
            return True  # Default to modern for unknown
        except:
            return True

    if is_modern(base_version):
        # Use standard .minecraft/assets
        return os.path.join(os.getenv("APPDATA"), ".minecraft", "assets")

    # Legacy versions get their own assets directory
    base = os.path.dirname(__file__)
    assets_dir = os.path.join(base, f"{base_version}_assets")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    return assets_dir
