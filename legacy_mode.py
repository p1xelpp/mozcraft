def is_legacy_version(version_id: str):
    # Minecraft versions always start with "1."
    if not version_id.startswith("1."):
        return False  # definitely NOT legacy

    try:
        # Extract base version (1.8.9 from "1.8.9-forge1.8.9-11.15.1.2318-1.8.9")
        base_version = version_id.split("-")[0]
        minor = int(base_version.split(".")[1])
    except:
        return False

    return minor <= 12
