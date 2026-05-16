# vulkanpatch.py
#ts sucks

def apply_vulkan_patch(jvm_args: list) -> list:
    """
    Voegt Vulkan‑mode flags toe aan de JVM‑argumenten.
    Dit forceert Minecraft om Vulkan te gebruiken i.p.v. OpenGL.
    """

    vulkan_flags = [
        "-Dminecraft.gl=disabled",        # no openGl
        "-Dminecraft.vulkan=true",        # yes vulkan
        "-Dorg.lwjgl.opengl.libname=disabled"  # no lwjgl u need to cheat on openGL
    ]

    # roger that
    return jvm_args + vulkan_flags
