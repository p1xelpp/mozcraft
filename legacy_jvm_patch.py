def apply_legacy_jvm_args(jvm_args, natives_path):
    jvm_args += [
        f"-Dorg.lwjgl.librarypath={natives_path}",
        f"-Dnet.java.games.input.librarypath={natives_path}",

        # Java 9+ module fixes
        "--add-opens=java.base/java.lang=ALL-UNNAMED",
        "--add-opens=java.base/java.io=ALL-UNNAMED",
        "--add-opens=java.base/java.nio=ALL-UNNAMED",
        "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",
        "--add-opens=java.desktop/sun.awt=ALL-UNNAMED",
        "--add-opens=java.desktop/sun.java2d=ALL-UNNAMED",

        # OpenGL compatibility
        "-Dorg.lwjgl.opengl.Display.allowSoftwareOpenGL=true"
    ]

    return jvm_args
