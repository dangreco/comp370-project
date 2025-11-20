import os


def in_github_actions() -> bool:
    return os.getenv("GITHUB_ACTIONS") == "true"
