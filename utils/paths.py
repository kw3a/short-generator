import os

def backgrounds_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backgrounds"))


def outputs_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))


def list_backgrounds():
    d = os.path.abspath(backgrounds_dir())
    if not os.path.isdir(d):
        return []
    return sorted([
        f for f in os.listdir(d)
        if os.path.isfile(os.path.join(d, f))
    ])
