# Introduction to ArrowBit

ArrowBit is a customizable programming language engine that empowers you to create your own domain-specific language (DSL) with minimal effort. You define commands in Python, and ArrowBit handles all the parsing, runtime management, and execution for you.

## Why ArrowBit?

Good if you have too much time to waste making useless things, but not enough time to fight with a complicated syntax

## Prerequisites

- Python 3.10 or higher

## Installation

Install ArrowBit via pip:

```shell
pip install arrowbit
```

## Your First Command

You can create a command using the `@arrowbit.command()` decorator (or the longer `@arrowbit.define_command()`):

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name = 'helloworld')
def my_first_command(env: arrowbit.Environment):
    print("Hello, World!")

repl.execute('helloworld')
```

**Output:**

```txt
Hello, World!
```

### How It Works

1. **Define the command**: Use the `@arrowbit.command()` decorator with a `name` parameter
2. **Environment parameter**: Your function always receives an `Environment` object as the first parameter
3. **Execute**: Use `repl.execute()` to run your command by name

## Command Parameters

### The Environment Parameter

**Every command function must accept at least one parameter of type `Environment`.** This is mandatory and always passed as the first argument.

The Environment object provides:

- Variable storage (`env.variables`)
- Read-only data (`env.readonly`)
- Result export (`env.export()`)
- Strict mode flag (`env.strict`)

### Custom Parameters

You can define additional parameters after the Environment parameter. ArrowBit supports:

- **String parameters** (`str`)
- **Integer parameters** (`int`)
- **Boolean parameters** (`bool`)
- **Optional parameters** with defaults

**Example with parameters:**

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name = 'say')
def say_command(env: arrowbit.Environment, content: str):
    print(content)

repl.execute('say -content "Hello!"')
```

**Output:**

```txt
Hello!
```

### Positional vs Named Parameters

ArrowBit supports both positional and named (flag-style) parameters:

```python
@arrowbit.command(name='greet')
def greet(env: arrowbit.Environment, name: str, greeting: str = "Hello"):
    print(f"{greeting}, {name}!")

# Both of these work:
repl.execute('greet "Alice" "Hi"')           # Positional
repl.execute('greet -name "Bob" -greeting "Hey"')  # Named
```

**Output:**

```txt
Hi, Alice!
Hey, Bob!
```

> **INFO:** You can mix positional and named parameters. Positional arguments are matched in order, while named arguments use the `-parameter value` syntax.

### Optional Parameters

Use Python's default values to make parameters optional:

```python
@arrowbit.command(name='log')
def log_command(env: arrowbit.Environment, message: str, level: str = "INFO"):
    print(f"[{level}] {message}")

repl.execute('log "Starting..."')                    # Uses default level
repl.execute('log "Critical error!" "ERROR"')        # Specifies level
```

**Output:**
```txt
[INFO] Starting...
[ERROR] Critical error!
```

## Working with the Environment

### Assigning Variables

```python
@arrowbit.command(name='setname')
def setname(env: arrowbit.Environment, name: str):
    env.assign('username', arrowbit.Object('STR', name))
    print(f"Username set to: {name}")
```

### Reading Variables

```python
@arrowbit.command(name='getname')
def getname(env: arrowbit.Environment):
    if 'username' in env.variables:
        print(f"Username: {env.variables['username'].value}")
    else:
        print("No username set")
```

### Exporting Values

Commands can return values by exporting them:

```python
@arrowbit.command(name='add')
def add(env: arrowbit.Environment, a: int, b: int):
    result = a + b
    env.export(arrowbit.Object('INT', result))
```

## Object Types

ArrowBit uses a typed object system:

```python
# Create objects
string_obj = arrowbit.Object('STR', 'hello')
int_obj = arrowbit.Object('INT', 42)
bool_obj = arrowbit.Object('BOOL', True)
list_obj = arrowbit.Object('LIST', [1, 2, 3])
null_obj = arrowbit.Object('NULL')

# Access values
value = string_obj.value  # 'hello'
type_name = string_obj.type  # 'STR'
```

**Available types:**
- `STR` - String values
- `INT` - Integer values
- `BOOL` - Boolean values
- `LIST` - List/array values
- `NULL` - Null/None values
- `VAR` - Variable references
- `CMD` - Command invocations
- `CONDITION` - Conditional expressions

## Context Flags

Commands can receive context flags using the `@flag` syntax:

```python
@arrowbit.command(name='print')
def print_cmd(env: arrowbit.Environment, text: str):
    ctx = env.readonly['ctx'].value
    
    if 'bold' in ctx:
        print(f"\033[1m{text}\033[0m")
    elif 'italic' in ctx:
        print(f"\033[3m{text}\033[0m")
    else:
        print(text)

# Usage:
repl.execute('print "Normal text"')
repl.execute('print @bold "Bold text"')
repl.execute('print @italic "Italic text"')
```

## Runtime and Execution

### Direct Execution

Execute single commands:

```python
from arrowbit import repl

result = repl.execute('mycommand "arg1" "arg2"')
```

### Script Execution

Run multi-line scripts:

```python
runtime = arrowbit.Runtime()
runtime.load("""
    say "Starting program..."
    setvar "count" "0"
    say "Program complete!"
""")
runtime.start()
```

### Interactive REPL

Start an interactive shell:

```python
from arrowbit import repl

@arrowbit.command(name='echo')
def echo(env: arrowbit.Environment, msg: str):
    print(msg)

repl.run()  # Starts interactive REPL
```

## Event Handlers

### Startup Handler

Execute code when the runtime starts:

```python
@arrowbit.on_start()
def startup(env: arrowbit.Environment):
    print("Application starting...")
    env.assign('initialized', arrowbit.Object('BOOL', True))
```

### Error Handler

Handle errors gracefully:

```python
@arrowbit.on_error()
def error_handler(env: arrowbit.Environment, err: arrowbit.errors.Error):
    print(f"Error: {err.title}")
    print(f"Message: {err.message}")
```

### Exit Handler

Clean up when the program exits:

```python
@arrowbit.on_exit()
def cleanup(env: arrowbit.Environment):
    print("Cleaning up resources...")
    # Save state, close files, etc.
```

## Error Handling

ArrowBit provides several built-in error types:

```python
from arrowbit import errors

@arrowbit.command(name='divide')
def divide(env: arrowbit.Environment, a: int, b: int):
    if b == 0:
        raise errors.Error("Division by zero is not allowed")
    
    print(a / b)
```

**Built-in errors:**
- `errors.Error` - Base error class
- `errors.UnknownName` - Variable or command not found
- `errors.MissingArgument` - Required argument not provided
- `errors.TooManyArguments` - Too many arguments provided
- `errors.InvalidArgument` - Invalid argument value
- `errors.UserCancel` - User cancelled operation (Ctrl+C)

## Complete Example

Here's a complete example demonstrating various features:

```python
import arrowbit
from arrowbit import repl, errors

# Define commands
@arrowbit.command(name='setvar')
def setvar(env: arrowbit.Environment, name: str, value: str):
    env.assign(name, arrowbit.Object('STR', value))
    print(f"✓ Variable '{name}' = '{value}'")

@arrowbit.command(name='getvar')
def getvar(env: arrowbit.Environment, name: str):
    if name in env.variables:
        print(env.variables[name].value)
    else:
        raise errors.UnknownName(name)

@arrowbit.command(name='echo')
def echo(env: arrowbit.Environment, message: str, uppercase: bool = False):
    output = message.upper() if uppercase else message
    print(output)

# Event handlers
@arrowbit.on_start()
def startup(env: arrowbit.Environment):
    print("=== ArrowBit Demo ===\n")

@arrowbit.on_error()
def handle_error(env: arrowbit.Environment, err: errors.Error):
    print(f"ERROR: {err.message}")

@arrowbit.on_exit()
def cleanup(env: arrowbit.Environment):
    print("\n=== Program ended ===")

# Execute commands
if __name__ == '__main__':
    repl.execute('setvar "username" "Alice"')
    repl.execute('echo "Hello, World!"')
    repl.execute('echo "loud message" true')
    repl.execute('getvar "username"')
```

**Output:**
```txt
=== ArrowBit Demo ===

✓ Variable 'username' = 'Alice'
Hello, World!
LOUD MESSAGE
Alice

=== Program ended ===
```

## Next Steps

Now that you understand the basics, explore these topics:

- **[Cogs](extensions/cogs.md)** - Organize commands into modular components
- **Runtime Management** - Advanced runtime configuration and control
- **Custom Parsers** - Extend ArrowBit's parsing capabilities
- **Type System** - Deep dive into ArrowBit's object types

## Tips and Best Practices

1. **Always include the Environment parameter** - It's required for all commands
2. **Use meaningful command names** - Make your DSL easy to understand
3. **Provide good defaults** - Use optional parameters with sensible defaults
4. **Handle errors gracefully** - Use `@on_error()` to provide helpful error messages
5. **Document your commands** - Use docstrings to explain what each command does
6. **Use Cogs for organization** - Group related commands together
7. **Test your commands** - Write tests to ensure your commands work correctly

## Common Patterns

### Input/Output Commands

```python
@arrowbit.command(name='ask')
def ask(env: arrowbit.Environment, prompt: str):
    answer = input(prompt)
    env.export(arrowbit.Object('STR', answer))
```

### File Operations

```python
@arrowbit.command(name='read')
def read_file(env: arrowbit.Environment, filename: str):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        env.export(arrowbit.Object('STR', content))
    except FileNotFoundError:
        raise errors.Error(f"File not found: {filename}")
```

### Conditional Logic

```python
@arrowbit.command(name='ifequal')
def if_equal(env: arrowbit.Environment, a: str, b: str, then: str):
    if a == b:
        repl.execute(then, env)
```

Happy coding with ArrowBit! 🚀
