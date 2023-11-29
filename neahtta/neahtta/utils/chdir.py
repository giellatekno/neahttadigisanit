from contextlib import contextmanager
from os import chdir, pathsep, environ
from pathlib import Path
from typing import Union


@contextmanager
def working_directory(path: Union[Path, str]):
    if not isinstance(path, Path):
        path = Path(path)

    origin = Path().absolute()
    if not path.is_absolute():
        path = origin / path

    try:
        chdir(path)
        yield
    finally:
        chdir(origin)


@contextmanager
def additional_paths(*paths: list[Union[Path, str]]):
    """Temporary prepend additional paths to the PATH environment variable,
    and restore the original PATH at the end of the context manager."""
    ps = []
    for i, p in enumerate(paths):
        if isinstance(p, Path):
            ps.append(str(p))
        elif isinstance(p, str):
            ps.append(p)
        else:
            msg = (
                "All arguments must be of type str or Path. "
                f"Argument {i} is {type(p)}"
            )
            raise TypeError(msg)

    old_path = environ["PATH"]

    try:
        environ["PATH"] = pathsep.join(ps) + pathsep + old_path
        yield
    finally:
        environ["PATH"] = old_path
