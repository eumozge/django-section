from glob import glob

import pytest


def get_paths(file_name):
    def normalize(path, name):
        return path.replace("/", ".").replace(f"{name}.py", name)

    return [
        normalize(path, file_name)
        for path in glob(f"**/{file_name}.py", recursive=True)
        if not (path.startswith("venv") or path.startswith(".venv"))
    ]


pytest_plugins = get_paths("fixtures") + get_paths("factories")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
