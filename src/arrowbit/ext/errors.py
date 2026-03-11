class Error(Exception):
    def __init__(self, message: str, title: str = "Error"):
        self.message = message
        self.title = title

        super().__init__(title + ": " + message)


class UserCancel(Error):
    def __init__(self):
        message = f"Runtime interrupted by user."
        super().__init__(message, "UserCancelError")


class InvalidSyntax(Error):
    def __init__(self, char: str, *position: int, **kwargs: str):
        if 'pre' in kwargs:
            print(kwargs['pre'])

        if len(position) >= 2:
            line, col = position[:2]
            message = f"Unexpected character '{char}' at line {line}, column {col}."
        elif len(position) == 1:
            message = f"Unexpected character '{char}' at  <{position[0]}>."
        else:
            message = f"Unexpected character '{char}'."

        super().__init__(message, "SyntaxError")

class UnknownName(Error):
    def __init__(self, name: str):
        message = f"Name '{name}' is not defined."
        super().__init__(message, "DefError")

class MissingArgument(Error):
    def __init__(self, path: str):
        message = f"One or more arguments is required but not defined in <{path}>."
        super().__init__(message, "DefError")

class TooManyArguments(Error):
    def __init__(self, path: str):
        message = f"One or more unexpected arguments in <{path}>."
        super().__init__(message, "DefError")

class InvalidArgument(Error):
    def __init__(self, name: str, _value: str = None, values_allowed: list = [], custom: str = None):
        message = f"Argument <{name}> is not valid."

        if len(values_allowed) > 0 and _value:
            message += " "

            if len(values_allowed) == 1:
                message += "Expected <" + values_allowed[0]
            else:
                message += "Expected <" + '> | <'.join(values_allowed)

            message += f">, got {_value}"
        elif custom:
            message += f" {custom}"

        super().__init__(message, "DefError")

class InvalidArgumentType(Error):
    def __init__(self, name: str, _type: str = None, types_allowed: list = [], custom: str = None):
        message = f"Argument <{name}> is not valid."

        if len(types_allowed) > 0 and _type:
            message += " "

            if len(types_allowed) == 1:
                message += "Expected <" + types_allowed[0]
            else:
                message += "Expected <" + '> | <'.join(types_allowed)

            message += f">, got {_type}"
        elif custom:
            message += f" {custom}"

        super().__init__(message, "DefError")

class Overflow(Error):
    def __init__(self):
        message = f"Tried to read a bigger splice of a value than its length."
        super().__init__(message, "ParseError")


class DecodeError(Error):
    def __init__(self, message: str):
        super().__init__(message, "DecodeError")