#!/usr/bin/env python3
import os
import sys

import environ


def main():
    env = environ.Env(DJANGO_DEBUG=(bool, False))
    env.read_env(os.getenv("ENV", ".env"))
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        env("DJANGO_SETTINGS_MODULE", default="app.config.settings.main"),
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
