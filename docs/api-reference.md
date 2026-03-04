# API Reference

Complete API documentation for ArrowBit.

## Core Decorators

### `@arrowbit.command(name: str)`

Alias: `@arrowbit.define_command(name: str)`

Define a new command that can be executed by ArrowBit.

**Parameters:**

- `name` (str): The name of the command

**Returns:**

- A decorator function

**Example:**

```python
@arrowbit.command(name = 'greet')
def greet_command(env: arrowbit.Environment, name: str):
    print(f"Hello, {name}!")
```

---

### `@arrowbit.on_start()`

Define a handler that executes when the runtime starts.

**Returns:**

- A decorator function

**Example:**

```python
@arrowbit.on_start()
def startup(env: arrowbit.Environment):
    print("Application starting...")
```

**Note:** Only triggered when `Runtime(main = True)`

---

### `@arrowbit.on_error()`

Define a handler that executes when an error occurs.

**Returns:**

- A decorator function

**Example:**

```python
@arrowbit.on_error()
def error_handler(env: arrowbit.Environment, err: arrowbit.errors.Error):
    print(f"Error: {err.message}")
```

**Note:** Only triggered when `Runtime(main = True)`

---

### `@arrowbit.on_exit()`

Define a handler that executes when the runtime exits.

**Returns:**

- A decorator function

**Example:**

```python
@arrowbit.on_exit()
def cleanup(env: arrowbit.Environment):
    print("Cleaning up...")
```

**Note:** Only triggered when `Runtime(main = True)`

---

## Classes

### Environment

**Constructor:**

```python
Environment(strict: bool = False)
```

Manages variables, state, and execution context.

**Parameters:**

- `strict` (bool): If `True`, variables must be declared before assignment. Default: `False`

**Attributes:**

- `variables` (dict[str, Object]): Dictionary of user-defined variables
- `readonly` (dict[str, Object]): Read-only context data (e.g., `ctx` for context flags)
- `strict` (bool): Whether strict mode is enabled
- `result` (Object): The last exported result

**Methods:**

#### `assign(name: str, obj: Object)`

Assign a value to a variable.

**Parameters:**

- `name` (str): Variable name
- `obj` (Object): Value to assign

**Raises:**

- `UnknownName`: If variable not declared in strict mode

**Example:**

```python
env.assign('username', arrowbit.Object('STR', 'Alice'))
```

---

#### `declare(name: str)`

Declare a variable (for strict mode).

**Parameters:**

- `name` (str): Variable name

**Example:**

```python
env = arrowbit.Environment(strict = True)
env.declare('count')
env.assign('count', arrowbit.Object('INT', 0))
```

---

#### `delete(name: str)`

Delete a variable.

**Parameters:**

- `name` (str): Variable name

**Raises:**

- `UnknownName`: If variable doesn't exist

**Example:**

```python
env.delete('temp_var')
```

---

#### `export(value: Object)`

Export a result from a command.

**Parameters:**

- `value` (Object): The value to export

**Example:**

```python
@arrowbit.command(name = 'add')
def add(env: Environment, a: int, b: int):
    result = a + b
    env.export(arrowbit.Object('INT', result))
```

---

#### `herit(env: Environment)`

Inherit settings and variables from another environment.

**Parameters:**

- `env` (Environment): The environment to inherit from

**Example:**

```python
child_env = arrowbit.Environment()
child_env.herit(parent_env)
```

---

### Runtime

**Constructor:**

```python
Runtime(main: bool = True)
```

Manages command execution and runtime lifecycle.

**Parameters:**

- `main` (bool): If `True`, triggers event handlers. Default: `True`

**Attributes:**

- `env` (Environment): The current environment
- `running` (bool): Whether the runtime is currently running
- `is_cycle` (bool): If `True`, loops through commands. Default: `True`
- `queue` (list[Command]): Queue of commands to execute
- `cycle` (int): Current cycle count (for looping)

**Methods:**

#### `load(file: str)`

Load a script into the runtime queue.

**Parameters:**

- `file` (str): Multi-line script to load

**Example:**

```python
runtime = arrowbit.Runtime()
runtime.load("""
    say "Hello"
    say "World"
""")
```

---

#### `start(env: Environment = None)`

Start executing the loaded script.

**Parameters:**

- `env` (Environment, optional): Environment to use. If not provided, uses `runtime.env`

**Raises:**

- `RuntimeError`: If runtime is already running

**Example:**

```python
env = arrowbit.Environment()
runtime.start(env)
```

---

#### `execute(seq: str, env: Environment = None)`

Execute a single command string.

**Parameters:**

- `seq` (str): Command string to execute
- `env` (Environment, optional): Environment to use

**Example:**

```python
runtime = arrowbit.Runtime()
runtime.execute('say "Hello"', env)
```

---

### Object

**Constructor:**

```python
Object(type: str, value: Any = 'null')
```

Represents a typed value in ArrowBit.

**Parameters:**

- `type` (str): The object type (STR, INT, BOOL, LIST, NULL, VAR, CMD, CONDITION)
- `value` (Any): The value. Default: `'null'`

**Attributes:**

- `id` (str): Unique identifier
- `type` (str): Object type
- `value` (Any): Object value

**Methods:**

#### `copy() -> Object`

Create a copy of the object.

**Returns:**

- A new Object instance

**Example:**

```python
obj1 = arrowbit.Object('STR', 'hello')
obj2 = obj1.copy()
```

---

**Object Types:**

| Type | Description | Example |
|------|-------------|---------|
| `STR` | String value | `Object('STR', 'hello')` |
| `INT` | Integer value | `Object('INT', 42)` |
| `BOOL` | Boolean value | `Object('BOOL', True)` |
| `LIST` | List/array value | `Object('LIST', [1, 2, 3])` |
| `NULL` | Null/None value | `Object('NULL')` |
| `VAR` | Variable reference | `Object('VAR', 'varname')` |
| `CMD` | Command invocation | `Object('CMD', command)` |
| `CONDITION` | Conditional expression | `Object('CONDITION', '<expr>')` |

---

### Cog

**Constructor:**

```python
Cog(env: Environment)
```

Base class for creating command groups.

**Parameters:**

- `env` (Environment): The environment to use

**Attributes:**

- `name` (str): The cog's namespace. Default: `'__main__'`
- `env` (Environment): The environment

**Methods:**

#### `setup()`

Define commands in this method. Must be implemented.

**Raises:**

- `NotImplementedError`: If not implemented

**Example:**

```python
class MyCog(arrowbit.cogs.Cog):
    def setup(self):
        @self.command('test')
        def test_cmd(env):
            print("Test")
```

---

#### `command(name: str)`

Decorator for defining a command within the cog.

**Parameters:**

- `name` (str): Command name (will be prefixed with cog name if not `__main__`)

**Returns:**

- A decorator function

**Example:**

```python
@self.command('hello')
def hello(env):
    print("Hello from cog!")
```

---

## Functions

### `arrowbit.cogs.load_cog(cog: Cog, name: str = '__main__')`

Load a cog into the runtime.

**Parameters:**

- `cog` (Cog): The cog instance to load
- `name` (str): Namespace for the cog. Default: `'__main__'`

**Raises:**

- `TypeError`: If cog is not a Cog instance

**Example:**

```python
cog = MyCog(env)
arrowbit.cogs.load_cog(cog, name = 'utils')
```

---

### `arrowbit.repl.execute(cmd: str | Command, strict: bool = True) -> Object | None`

Execute a single command.

**Parameters:**

- `cmd` (str | Command): Command to execute
- `strict` (bool): Enable strict mode. Default: `True`

**Returns:**

- The exported result, or `None`

**Example:**

```python
result = arrowbit.repl.execute('add 5 10')
```

---

### `arrowbit.repl.run()`

Start an interactive REPL session.

**Example:**

```python
arrowbit.repl.run()
```

**Note:** Requires commands to be defined before calling.

---

## Errors

All errors inherit from `arrowbit.errors.Error`.

### Base Error

```python
class Error(Exception):
    def __init__(self, message: str, title: str = "Error")
```

**Attributes:**

- `message` (str): Error message
- `title` (str): Error title/type

---

### `UnknownName`

Raised when a variable or command is not defined.

**Constructor:**

```python
UnknownName(name: str)
```

**Example:**

```python
raise arrowbit.errors.UnknownName('undefined_var')
```

---

### `MissingArgument`

Raised when a required argument is missing.

**Constructor:**

```python
MissingArgument(path: str)
```

**Example:**

```python
raise arrowbit.errors.MissingArgument('mycommand')
```

---

### `TooManyArguments`

Raised when too many arguments are provided.

**Constructor:**

```python
TooManyArguments(path: str)
```

---

### `InvalidArgument`

Raised when an argument has an invalid value.

**Constructor:**

```python
InvalidArgument(name: str, value: str = None, values_allowed: list = [], custom: str = None)
```

**Parameters:**

- `name` (str): Argument name
- `value` (str): The invalid value
- `values_allowed` (list): List of allowed values
- `custom` (str): Custom error message

**Example:**

```python
raise arrowbit.errors.InvalidArgument('type', 'INVALID', ['STR', 'INT', 'BOOL'])
```

---

### `InvalidArgumentType`

Raised when an argument has an invalid type.

**Constructor:**

```python
InvalidArgumentType(name: str, type: str = None, types_allowed: list = [], custom: str = None)
```

---

### `UserCancel`

Raised when the user cancels execution (Ctrl+C).

**Constructor:**

```python
UserCancel()
```

---

### `InvalidSyntax`

Raised when syntax is invalid.

**Constructor:**

```python
InvalidSyntax(char: str, position: int)
```

---

### `Overflow`

Raised when trying to read beyond a value's length.

**Constructor:**

```python
Overflow()
```

---

### `DecodeError`

Raised when decoding fails.

**Constructor:**

```python
DecodeError(message: str)
```

---

## Constants

### `arrowbit.VERSION`

Current version of ArrowBit.

**Type:** `str`

**Example:**

```python
print(f"ArrowBit v{arrowbit.VERSION}")
```

---

### `arrowbit.default_env`

Default environment instance.

**Type:** `Environment`

**Example:**

```python
arrowbit.default_env.assign('global', arrowbit.Object('STR', 'value'))
```

---

## Module Structure

```tree
arrowbit/
├── __init__.py          # Main exports
├── repl.py              # REPL functionality
└── ext/
    ├── commands.py      # Command decorator
    ├── runtime.py       # Runtime and Environment
    ├── cogs.py          # Cogs system
    ├── parser.py        # Parser and Object classes
    ├── errors.py        # Error classes
    ├── logger.py        # Logging utilities
    └── utils.py         # Utility functions
```

## Import Patterns

### Recommended Imports

```python
# Full import
import arrowbit

# Specific imports
from arrowbit import Environment, Runtime, Object
from arrowbit import repl, cogs, errors
```

### Available from Main Module

```python
arrowbit.command          # Command decorator
arrowbit.define_command   # Command decorator (long form)
arrowbit.cogs             # Cogs module
arrowbit.Runtime          # Runtime class
arrowbit.Environment      # Environment class
arrowbit.default_env      # Default environment
arrowbit.on_error         # Error handler decorator
arrowbit.on_start         # Start handler decorator
arrowbit.on_exit          # Exit handler decorator
arrowbit.Object           # Object class
arrowbit.errors           # Errors module
arrowbit.VERSION          # Version string
```

## Type Hints

ArrowBit supports type hints for better IDE support:

```python
from typing import Optional
import arrowbit

def my_command_handler(
    env: arrowbit.Environment,
    name: str,
    count: int = 0,
    verbose: bool = False
) -> Optional[arrowbit.Object]:
    # Command implementation
    result = process_data(name, count, verbose)
    env.export(arrowbit.Object('STR', result))
    return env.result
```
