# ArrowBit Documentation

Welcome to the complete documentation for ArrowBit - a customizable programming language engine for Python.

## Table of Contents

### Getting Started

- **[Introduction](introduction.md)** - Get started with ArrowBit, learn the basics, and create your first commands
  - Installation
  - First command
  - Parameters
  - Environment basics
  - Event handlers

### Core Concepts

- **[Runtime Management](runtime.md)** - Deep dive into Runtime and Environment classes
  - Runtime class
  - Environment class
  - Variable management
  - Execution strategies
  - Event lifecycle
  - Best practices

- **[Cogs Extension](extensions/cogs.md)** - Organize commands with the Cogs system
  - What are Cogs
  - Creating Cogs
  - Loading Cogs
  - Namespacing
  - Best practices

### Reference

- **[API Reference](api-reference.md)** - Complete API documentation
  - Decorators
  - Classes
  - Functions
  - Error types
  - Constants
  - Type hints

### Practical Guides

- **[Examples and Use Cases](examples.md)** - Real-world examples and applications
  - Simple Calculator
  - File Manager
  - Task Runner
  - Interactive Quiz
  - Configuration Manager
  - Mini Programming Language
  - Command-Line Tool

## Quick Links

### Common Tasks

- [Define a command](introduction.md#create-your-first-command)
- [Work with parameters](introduction.md#command-parameters)
- [Manage variables](runtime.md#working-with-variables)
- [Handle errors](introduction.md#error-handling)
- [Create a Cog](extensions/cogs.md#creating-a-cog)
- [Run a REPL](introduction.md#interactive-repl)

### API Quick Reference

```python
# Import ArrowBit
import arrowbit
from arrowbit import Environment, Runtime, Object, repl, cogs, errors

# Define a command
@arrowbit.command(name='mycommand')
def my_command(env: Environment, param: str):
    print(param)

# Create environment
env = Environment(strict=False)

# Execute command
repl.execute('mycommand "Hello"')

# Create a Cog
class MyCog(cogs.Cog):
    def setup(self):
        @self.command('test')
        def test(env: Environment):
            print("Test")

# Load Cog
cogs.load_cog(MyCog(env), name='my')
```

## Feature Overview

### ✨ Core Features

- **Custom Command Definition** - Define commands using Python decorators
- **Flexible Parameters** - Support for positional and named parameters
- **Type System** - Built-in object types (STR, INT, BOOL, LIST, etc.)
- **Variable Management** - Built-in variable system with strict mode
- **Cogs Organization** - Modular command grouping
- **Event Hooks** - Handle startup, errors, and exit events
- **REPL Support** - Interactive command execution
- **Context Flags** - Pass contextual information to commands

### 📦 What's Included

```tree
arrowbit/
├── Core
│   ├── Command decorator (@arrowbit.command)
│   ├── Environment class
│   └── Runtime class
├── Extensions
│   ├── Cogs system
│   └── REPL
├── Utilities
│   ├── Parser
│   ├── Object system
│   └── Error handling
└── Event System
    ├── on_start()
    ├── on_error()
    └── on_exit()
```

## Example Use Cases

ArrowBit is perfect for:

- 🎯 **Domain-Specific Languages** - Create custom languages for specific tasks
- 🛠️ **Command-Line Tools** - Build interactive CLI applications
- 📚 **Educational Tools** - Teach programming concepts
- 🤖 **Automation Scripts** - Create custom scripting environments
- 🎮 **Game Scripting** - Build in-game command systems
- ⚙️ **Configuration Systems** - Manage application settings

## Learning Path

### Beginner

1. Read the [Introduction](introduction.md)
2. Follow the "Your First Command" example
3. Experiment with parameters
4. Learn about the Environment

### Intermediate

1. Study [Runtime Management](runtime.md)
2. Create your first [Cog](extensions/cogs.md)
3. Implement error handling
4. Build a simple calculator or file manager

### Advanced

1. Review the [API Reference](api-reference.md)
2. Study complex [Examples](examples.md)
3. Build a complete DSL
4. Create reusable Cog libraries

## Code Examples

### Minimal Example

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name='hello')
def hello(env: arrowbit.Environment):
    print("Hello, World!")

repl.execute('hello')
```

### With Parameters

```python
@arrowbit.command(name='greet')
def greet(env: arrowbit.Environment, name: str, greeting: str = "Hello"):
    print(f"{greeting}, {name}!")

repl.execute('greet "Alice"')           # Hello, Alice!
repl.execute('greet "Bob" "Hi"')        # Hi, Bob!
```

### Using Cogs

```python
from arrowbit import cogs, Environment

class UtilsCog(cogs.Cog):
    def setup(self):
        @self.command('echo')
        def echo(env: Environment, msg: str):
            print(msg)

env = arrowbit.Environment()
cogs.load_cog(UtilsCog(env), name='utils')

repl.execute('utils.echo "Test"')  # Test
```

### With Variables

```python
@arrowbit.command(name='set')
def set_var(env: Environment, name: str, value: str):
    env.assign(name, arrowbit.Object('STR', value))

@arrowbit.command(name='get')
def get_var(env: Environment, name: str):
    if name in env.variables:
        print(env.variables[name].value)

repl.execute('set "username" "Alice"')
repl.execute('get "username"')  # Alice
```

## Version Information

This documentation is for **ArrowBit v1.0.0**

- **Python Version**: 3.10 or higher
- **License**: See [LICENSE](../LICENSE)
- **Repository**: [GitHub](https://github.com/ejnalo/ArrowBit)

## Getting Help

- 📖 **Documentation**: You're reading it!
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/ejnalo/ArrowBit/issues)
- 💬 **Questions**: Ask questions in GitHub Discussions
- 📧 **Contact**: Check the repository for contact information

## Contributing

Contributions are welcome! Areas where you can help:

- 📝 Improve documentation
- 🐛 Fix bugs
- ✨ Add new features
- 🧪 Write tests
- 💡 Share examples

## Next Steps

Ready to get started?

👉 **[Begin with the Introduction →](introduction.md)**

Or jump directly to:

- [Create your first command](introduction.md#create-your-first-command)
- [Learn about Cogs](extensions/cogs.md)
- [See practical examples](examples.md)
- [Browse the API Reference](api-reference.md)

_Happy coding with ArrowBit! 🚀_
