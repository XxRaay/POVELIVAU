import os
from pov_modules import register_module


def path_exists(path: str) -> bool:
    return os.path.exists(path)


register_module('is', {
    'path_exists': path_exists,
})
