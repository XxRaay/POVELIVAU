import os
import shutil

from errors import PovelRuntimeError
from pov_modules import register_module


def list_dir():
    try:
        return os.listdir()
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось обозреть владения: {exc}")


def get_cwd() -> str:
    try:
        return os.getcwd()
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось узреть имя земли текущей: {exc}")


def path_exists(path: str) -> bool:
    return os.path.exists(path)


def change_dir(path: str):
    try:
        os.chdir(path)
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось сменить землю на '{path}': {exc}")


def make_dir(path: str):
    try:
        os.mkdir(path)
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось возвести чертог '{path}': {exc}")


def remove_tree(path: str):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        raise PovelRuntimeError(f"Чертог '{path}' не обретается в сих землях!")
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось предать забвению чертог '{path}': {exc}")


def remove_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        raise PovelRuntimeError(f"Свиток '{path}' не найден в землях!")
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось изгнать свиток '{path}': {exc}")


def rename_file(src: str, dst: str):
    try:
        os.rename(src, dst)
    except FileNotFoundError:
        raise PovelRuntimeError(f"Грамота '{src}' не найдена для переименования!")
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось переименовать грамоту '{src}' в '{dst}': {exc}")


def append_text(path: str, text: str):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
    except OSError as exc:
        raise PovelRuntimeError(f"Не удалось вписать в свиток '{path}': {exc}")


register_module('земли', {
    'list_dir': list_dir,
    'get_cwd': get_cwd,
    'path_exists': path_exists,
    'change_dir': change_dir,
    'make_dir': make_dir,
    'remove_tree': remove_tree,
    'remove_file': remove_file,
    'rename_file': rename_file,
    'append_text': append_text,
})
