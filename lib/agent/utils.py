import functools
from prompt_toolkit.application import run_in_terminal

def flatten(items):
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item

def output_reader(handler, callback, *args):
    for line in iter(handler.readline, b""):
        if not line:
            break
        run_in_terminal(functools.partial(callback, line, *args))
