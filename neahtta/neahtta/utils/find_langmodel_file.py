import os

SEARCH_PATHS = os.environ.get(
    "LANGMODELS",
    # 1. path on gtdict, 2. apertium-nightly, 3. locally compiled `make install`
    "/opt/smi:/usr/share/giella:/usr/local/share/giella",
).split(os.pathsep)


def find_langmodel_file(file_path: str):
    for search_path in SEARCH_PATHS:
        full_path = os.path.join(search_path, file_path)
        if os.path.exists(full_path):
            return full_path
