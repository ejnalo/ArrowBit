from .errors import Error

def log(message: str):
    print(message)

def error(error: str | Error):
    if isinstance(error, Error):
        print(f"\033[31m{error.title}:\033[0m {error.message}")
    else:
        print(f"\033[31m[ERROR]\033[0m {error}")

def warn(message: str):
    print(f"\033[33m[WARN]\033[0m {message}")

def info(message: str):
    print(f"\033[34m[INFO]\033[0m {message}")