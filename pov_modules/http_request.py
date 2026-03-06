import requests
from errors import PovelRuntimeError
from pov_modules import register_module, register_node_handler


def http_get(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        raise PovelRuntimeError(
            f"Вестник не смог достигнуть земель по адресу '{url}': {exc}"
        )
    return response.text


def http_post(url: str, body) -> str:
    try:
        response = requests.post(url, data=str(body), timeout=5)
    except requests.RequestException as exc:
        raise PovelRuntimeError(
            f"Вестник с вестью не дошёл до земель по адресу '{url}': {exc}"
        )
    return response.text


register_module('http request', {
    'http_get': http_get,
    'http_post': http_post,
})


def _handle_http_get(interpreter, node):
    url = interpreter.execute(node.url)
    return http_get(url)


def _handle_http_post(interpreter, node):
    url = interpreter.execute(node.url)
    body = interpreter.execute(node.body)
    return http_post(url, body)


register_node_handler('HttpGetNode', _handle_http_get)
register_node_handler('HttpPostNode', _handle_http_post)
