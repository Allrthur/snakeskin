from pathlib import Path

def absolute_path(path:str):
    return Path(__file__).parent.joinpath(path)