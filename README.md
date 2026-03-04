# ArrowBit

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**ArrowBit** is a customizable programming language engine that allows you to create your own domain-specific language (DSL) in Python. Define your commands once in Python, and ArrowBit handles all the parsing, execution, and runtime management for you.

## ✨ Features

- **Custom Command Definition**: Define commands using simple Python decorators
- **Flexible Parameter Handling**: Support for positional and named parameters
- **Environment & Variables**: Built-in variable system with strict mode support
- **Cogs System**: Organize commands into modular, reusable components
- **Runtime Hooks**: Handle errors, startup, and exit events with custom handlers
- **REPL Support**: Built-in Read-Eval-Print Loop for interactive development
- **Context Flags**: Pass contextual information to commands
- **Object System**: Type-safe object handling (STR, INT, BOOL, LIST, etc.)

## 📋 Prerequisites

- Python 3.10 or higher

## 🚀 Installation

Install ArrowBit via pip:

```shell
pip install arrowbit
```

## 📖 Quick Start

### Your First Command

Create a simple "Hello, World!" command:

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name='helloworld')
def my_first_command(env: arrowbit.Environment):
    print("Hello, World!")

repl.execute('helloworld')
```

**Output:**
```
Hello, World!
```

### Commands with Parameters

Commands can accept parameters:

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name='greet')
def greet_command(env: arrowbit.Environment, name: str):
    print(f"Hello, {name}!")

repl.execute('greet "Alice"')  # Using named parameter
repl.execute('greet -name "Bob"')  # Using flag parameter
```

**Output:**
```
Hello, Alice!
Hello, Bob!
```

### Working with Variables

ArrowBit has a built-in variable system:

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name='setvar')
def setvar(env: arrowbit.Environment, name: str, value: str):
    env.assign(name, arrowbit.Object('STR', value))
    print(f"Variable '{name}' set to: {value}")

@arrowbit.command(name='getvar')
def getvar(env: arrowbit.Environment, name: str):
    if name in env.variables:
        print(env.variables[name].value)

repl.execute('setvar "username" "Alice"')
repl.execute('getvar "username"')
```

## 🎯 Core Concepts

### Environment

The `Environment` class manages variables and execution state:

```python
env = arrowbit.Environment(strict=False)

# Assign variables
env.assign('myvar', arrowbit.Object('INT', 42))

# Access variables
value = env.variables['myvar'].value  # 42

# Export values from commands
env.export(arrowbit.Object('STR', 'result'))
```

### Runtime

The `Runtime` class manages command execution:

```python
runtime = arrowbit.Runtime()
runtime.load("""
    say "Starting program..."
    greet "World"
    say "Program complete!"
""")
runtime.start(env)
```

### Object Types

ArrowBit supports various object types:

- `STR`: String values
- `INT`: Integer values  
- `BOOL`: Boolean values
- `LIST`: List/array values
- `NULL`: Null/None values
- `VAR`: Variable references
- `CMD`: Command invocations
- `CONDITION`: Conditional expressions

### Event Handlers

Handle runtime events with decorators:

```python
@arrowbit.on_start()
def startup(env: arrowbit.Environment):
    print("Program starting...")

@arrowbit.on_error()
def error_handler(env: arrowbit.Environment, err: arrowbit.errors.Error):
    print(f"Error occurred: {err.message}")

@arrowbit.on_exit()
def cleanup(env: arrowbit.Environment):
    print("Program exiting...")
```

## 🔧 Organizing with Cogs

For larger projects, use Cogs to organize commands:

```python
import arrowbit
from arrowbit import cogs, Environment

class UtilitiesCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
    
    def setup(self):
        @self.command('add')
        def add_cmd(env: Environment, a: int, b: int):
            result = a + b
            print(f"Result: {result}")
            env.export(arrowbit.Object('INT', result))
        
        @self.command('echo')
        def echo_cmd(env: Environment, message: str):
            print(message)

# Load the cog
env = arrowbit.Environment()
cogs.load_cog(UtilitiesCog(env), name='utils')

# Use commands
from arrowbit import repl
repl.execute('utils.add 5 3')      # Result: 8
repl.execute('utils.echo "Hi!"')   # Hi!
```

## 🎨 Context Flags

Commands can use context flags for conditional behavior:

```python
@arrowbit.command(name='say')
def say(env: arrowbit.Environment, content: str):
    is_bold = 'bold' in env.readonly['ctx'].value
    
    if is_bold:
        print(f"\033[1m{content}\033[0m")
    else:
        print(content)

# Usage with context flag
repl.execute('say -content "Normal text"')
repl.execute('say @bold -content "Bold text"')
```

## 📚 Documentation

- [Introduction](docs/introduction.md) - Getting started guide
- [Cogs Extension](docs/extensions/cogs.md) - Detailed Cogs documentation

## 🔍 Example Projects

### Simple Calculator

```python
import arrowbit
from arrowbit import cogs, Environment

class CalcCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
    
    def setup(self):
        @self.command('add')
        def add(env: Environment, a: int, b: int):
            print(a + b)
        
        @self.command('subtract')
        def subtract(env: Environment, a: int, b: int):
            print(a - b)
        
        @self.command('multiply')
        def multiply(env: Environment, a: int, b: int):
            print(a * b)

env = arrowbit.Environment()
cogs.load_cog(CalcCog(env), name='calc')
```

### Interactive REPL

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name='echo')
def echo(env: arrowbit.Environment, message: str):
    print(message)

@arrowbit.on_start()
def startup(env: arrowbit.Environment):
    print("Welcome to My REPL!")

repl.run()  # Starts interactive REPL
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🔗 Links

- **Repository**: [ArrowBit on GitHub](https://github.com/ejnalo/ArrowBit)
- **Issues**: [Report a bug](https://github.com/ejnalo/ArrowBit/issues)

## 💡 Use Cases

ArrowBit is perfect for:

- Creating custom scripting languages for specific domains
- Building command-line tools with custom syntax
- Developing educational programming environments
- Prototyping domain-specific languages (DSLs)
- Creating interactive shells for applications

---

Made with ❤️ by Loan
