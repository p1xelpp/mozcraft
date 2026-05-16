# offlinepatch.py

def apply_offline_patch(jvm_args: list) -> list:
    """
    Zet de interne singleplayer server in offline-mode.
    Hierdoor werkt singleplayer zonder Microsoft-auth.
    """
    offline_flags = [
        "-Dminecraft.server.online-mode=false",
        "-Dminecraft.api.auth.host=offline",
        "-Dminecraft.api.session.host=offline",
        "-Dminecraft.api.services.host=offline"
    ]
    return jvm_args + offline_flags
