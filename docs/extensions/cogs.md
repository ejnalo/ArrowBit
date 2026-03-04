# ArrowBit Cogs

Cogs are a system that permits you to group your commands smartly. They provide a clean and organized way to structure your ArrowBit commands, making your codebase more maintainable and modular.

## What are Cogs?

A Cog is a class that inherits from `arrowbit.cogs.Cog` and contains a `setup()` method where you define all your commands. Cogs are particularly useful when you want to:

- **Group related commands together** (e.g., math commands, file commands, utility commands)
- **Organize large projects** with many commands
- **Separate concerns** in your application
- **Make your code more maintainable** and easier to navigate

## Creating a Cog

To create a Cog, you need to:

1. Import the necessary modules
2. Create a class that inherits from `arrowbit.cogs.Cog`
3. Implement the `setup()` method
4. Define your commands inside the `setup()` method, using
5. Load the Cog using `arrowbit.cogs.load_cog()`

### Basic Example

```python
import arrowbit
from arrowbit import cogs, Environment

class MyCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @self.command(name = 'hello')
        def hello_command(env: Environment):
            print("Hello from my cog!")

        @self.command(name = 'goodbye')
        def goodbye_command(env: Environment):
            print("Goodbye!")

# Load the cog
cogs.load_cog(MyCog(arrowbit.default_env))
```

**Warning:** The Cog class has its own `command` decorator. Please use it instead of the basic `commands.command` decorator, otherwise the command will be considered as independant.

## The Cog Class

### Constructor

Every Cog must call the parent constructor with an `Environment` object:

```python
def __init__(self, env: Environment):
    super().__init__(env)
```

### The setup() Method

The `setup()` method is where you define all your commands. This method is called when the Cog is loaded:

```python
def setup(self):
    @self.command(name = 'mycommand')
    def my_command(env: Environment):
        # Command logic here
        pass
```

## Loading Cogs

To load a Cog into your ArrowBit runtime, use the `load_cog()` function:

```python
from arrowbit import cogs

# Load a cog with default name
cogs.load_cog(MyCog(env))

# Load a cog with a custom namespace
cogs.load_cog(MyCog(env), name = 'utils')
```

### Cog Namespaces

When you provide a name to `load_cog()`, all commands in that Cog will be prefixed with the namespace:

```python
class UtilsCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @self.command('clear')
        def clear_command(env: Environment):
            print("Clearing...")

# Load with namespace
cogs.load_cog(UtilsCog(env), name='utils')

# Now the command is accessible as 'utils.clear'
```

**Note:** When using `self.command()` within a Cog, the command name will automatically be prefixed with the Cog's namespace.

## Complete Example

Here's a comprehensive example showing how to create and use Cogs:

```python
import arrowbit
from arrowbit import cogs, Environment, errors

class MathCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @self.command('add')
        def add_command(env: Environment, a: int, b: int):
            result = a + b
            print(f"{a} + {b} = {result}")
            env.export(arrowbit.Object('INT', result))

        @self.command('multiply')
        def multiply_command(env: Environment, a: int, b: int):
            result = a * b
            print(f"{a} × {b} = {result}")
            env.export(arrowbit.Object('INT', result))

class StringCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @self.command('upper')
        def upper_command(env: Environment, text: str):
            result = text.upper()
            print(result)
            env.export(arrowbit.Object('STR', result))

        @self.command('lower')
        def lower_command(env: Environment, text: str):
            result = text.lower()
            print(result)
            env.export(arrowbit.Object('STR', result))

# Create environment
env = arrowbit.Environment()

# Load cogs with namespaces
cogs.load_cog(MathCog(env), name = 'math')
cogs.load_cog(StringCog(env), name = 'string')

# Use the commands
from arrowbit import repl

repl.execute('math.add 5 10')           # Output: 5 + 10 = 15
repl.execute('math.multiply 3 4')       # Output: 3 × 4 = 12
repl.execute('string.upper "hello"')    # Output: HELLO
repl.execute('string.lower "WORLD"')    # Output: world
```

## Best Practices

1. **One Cog per file**: Keep each Cog in its own file for better organization
2. **Logical grouping**: Group related commands together in a Cog
3. **Descriptive names**: Use clear, descriptive names for your Cogs and namespaces
4. **Initialize properly**: Always call `super().__init__(env)` in your Cog's constructor
5. **Use namespaces**: When loading multiple Cogs, use meaningful namespaces to avoid command name conflicts

## Common Patterns

### Error Handling in Cogs

```python
class SafeCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @arrowbit.on_error()
        def handle_error(env: Environment, err: errors.Error):
            print(f"Error: {err.message}")

        @self.command('divide')
        def divide_command(env: Environment, a: int, b: int):
            if b == 0:
                raise errors.Error("Cannot divide by zero")
            print(f"{a} / {b} = {a / b}")
```

### Using Environment Variables

```python
class VarCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @self.command('setvar')
        def setvar_command(env: Environment, name: str, value: str):
            env.assign(name, arrowbit.Object('STR', value))

        @self.command('getvar')
        def getvar_command(env: Environment, name: str):
            if name in env.variables:
                print(env.variables[name].value)
            else:
                raise errors.UnknownName(name)
```

## Cog vs Regular Commands

You can use regular commands without Cogs for simple scripts, but Cogs are recommended when:

- Your project has more than 5-10 commands
- You want to organize commands by functionality
- You're building a reusable library of commands
- You need better code organization

### Without Cogs (Simple)

```python
import arrowbit

@arrowbit.command('hello')
def hello(env: arrowbit.Environment):
    print("Hello!")
```

### With Cogs (Organized)

```python
import arrowbit
from arrowbit import cogs, Environment

class GreetingsCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)

    def setup(self):
        @self.command('hello')
        def hello(env: Environment):
            print("Hello!")

cogs.load_cog(GreetingsCog(arrowbit.default_env), name = 'greetings')
```
