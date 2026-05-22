# legacy_args.py

def get_legacy_args(data):
    """
    Geeft jvm_args en game_args terug voor oude versies zoals 1.8.9
    """

    # 1.8.9 has no JVM arguments, only game arguments in a single string
    jvm_args = []

    # 1.8.9 uses minecraftArguments (string)
    raw = data["minecraftArguments"]
    game_args = raw.split(" ")

    return jvm_args, game_args
