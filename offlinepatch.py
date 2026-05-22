# offlinepatch.py

def apply_offline_patch(jvm_args: list) -> list:
    """
    Zet de interne singleplayer server in offline-mode.
    Hierdoor werkt singleplayer zonder Microsoft-auth.
    """
    offline_flags = [
        "-Dminecraft.server.online-mode=false",
        "-Dminecraft.api.auth.host=http://offline",
        "-Dminecraft.api.session.host=http://offline",
        "-Dminecraft.api.services.host=http://offline",
        "-Dminecraft.api.profiles.host=http://offline"
    ]
    return jvm_args + offline_flags
