# vulkanpatch.py
#
# This file adds Vulkan-mode JVM flags to your launcher.
# You use this as a library: import and then apply_vulkan_patch(jvm_args)

def apply_vulkan_patch(jvm_args: list) -> list:
    """
    Adds Vulkan-mode flags to JVM arguments.
    This forces Minecraft to use Vulkan instead of OpenGL.
    """

    vulkan_flags = [
        "-Dminecraft.gl=disabled",        # Disable OpenGL
        "-Dminecraft.vulkan=true",        # Force Vulkan backend
        "-Dorg.lwjgl.opengl.libname=disabled"  # LWJGL must not load GL libs
    ]

    # Add to existing JVM args
    return jvm_args + vulkan_flags
