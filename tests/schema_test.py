from glob import iglob
from os.path import splitext, basename
import importlib

from src.utils import validate_module


def test_ext_schemas():
    for ext in iglob("src/extensions/*"):
        name = splitext(basename(ext))[0]
        module = importlib.import_module(f"src.extensions.{name}")
        validate_module(module)
        del module


if __name__ == "__main__":
    test_ext_schemas()
