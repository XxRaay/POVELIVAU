import os
import shutil

from errors import PovelRuntimeError
from pov_modules import register_module, register_node_handler


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


def _handle_list_dir(_interpreter, _node):
    return list_dir()


def _handle_cwd(_interpreter, _node):
    return get_cwd()


def _handle_path_exists(interpreter, node):
    path = str(interpreter.execute(node.path))
    return path_exists(path)


def _handle_chdir(interpreter, node):
    path = str(interpreter.execute(node.path))
    change_dir(path)


def _handle_mkdir(interpreter, node):
    path = str(interpreter.execute(node.path))
    make_dir(path)


def _handle_rmtree(interpreter, node):
    path = str(interpreter.execute(node.path))
    remove_tree(path)


def _handle_remove(interpreter, node):
    path = str(interpreter.execute(node.path))
    remove_file(path)


def _handle_rename(interpreter, node):
    src = str(interpreter.execute(node.src))
    dst = str(interpreter.execute(node.dst))
    rename_file(src, dst)


def _handle_file_write(interpreter, node):
    path = str(interpreter.execute(node.path))
    text = str(interpreter.execute(node.text))
    append_text(path, text)


register_node_handler('ListDirNode', _handle_list_dir)
register_node_handler('CwdNode', _handle_cwd)
register_node_handler('PathExistsNode', _handle_path_exists)
register_node_handler('ChdirNode', _handle_chdir)
register_node_handler('MkdirNode', _handle_mkdir)
register_node_handler('RmtreeNode', _handle_rmtree)
register_node_handler('RemoveNode', _handle_remove)
register_node_handler('RenameNode', _handle_rename)
register_node_handler('FileWriteNode', _handle_file_write)
