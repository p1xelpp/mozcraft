# argpatch.py

def substitute_args(args: list, values: dict) -> list:
    """
    Vervangt alle ${...} variabelen in Minecraft arguments.
    """
    out = []
    for arg in args:
        if isinstance(arg, str):
            for key, val in values.items():
                arg = arg.replace("${" + key + "}", val)
        out.append(arg)
    return out
