from java_detect import find_java17, find_java21

def select_modern_java(version_id: str):
    """
    Selects the correct Java version for modern Minecraft.
    1.17 → 1.20.4 = Java 17
    1.20.5+ = Java 21
    """

    # Extract major version (e.g. "1.20.5" → 20)
    try:
        major = int(version_id.split(".")[1])
    except:
        major = 20  # fallback

    # 1.17 → 1.20.4 → Java 17
    if 17 <= major <= 20:
        java = find_java17()
        if java:
            return java

    # 1.20.5+ → Java 21
    java = find_java21()
    if java:
        return java

    # Fallback: try Java 17 anyway
    java = find_java17()
    if java:
        return java

    # If nothing found, fallback to system java
    return "java"
