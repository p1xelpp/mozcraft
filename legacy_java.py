from java_detect import find_java8, find_java17, find_java21

def select_legacy_java():
    # Prefer Java 8
    java = find_java8()
    if java:
        return java

    # Java 17 works with patches
    java = find_java17()
    if java:
        return java

    # Java 21 also works with patches
    java = find_java21()
    if java:
        return java

    return None
