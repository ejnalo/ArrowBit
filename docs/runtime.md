# Runtime Management

The Runtime system in ArrowBit manages the execution of commands, handling the parsing, variable management, and execution flow. This guide covers the Runtime class, Environment class, and execution strategies.

## The Runtime Class

The `Runtime` class is responsible for executing ArrowBit commands and managing the execution lifecycle.

### Creating a Runtime

```python
import arrowbit

# Create a runtime instance
runtime = arrowbit.Runtime(main=True)

# Create with custom environment
env = arrowbit.Environment(strict=True)
runtime = arrowbit.Runtime(main=True)
```

**Parameters:**

- `main` (bool): If `True`, triggers `on_start`, `on_error`, and `on_exit` event handlers. Default: `True`

### Loading Scripts

Use the `load()` method to load a multi-line script:

```python
runtime = arrowbit.Runtime()

script = """
say "Starting program"
setvar "count" "0"
say "Program loaded"
"""

runtime.load(script)
```

### Starting Execution

Execute the loaded script with the `start()` method:

```python
env = arrowbit.Environment()
runtime.start(env)
```

**Parameters:**
- `env` (Environment, optional): The environment to use for execution. If not provided, uses the runtime's default environment.

### Complete Example

```python
import arrowbit

@arrowbit.command(name='say')
def say(env: arrowbit.Environment, message: str):
    print(message)

@arrowbit.command(name='add')
def add(env: arrowbit.Environment, a: int, b: int):
    result = a + b
    print(f"Result: {result}")
    env.export(arrowbit.Object('INT', result))

# Create and configure runtime
runtime = arrowbit.Runtime()
runtime.load("""
say "Starting calculation"
add 10 20
say "Calculation complete"
""")

# Execute
env = arrowbit.Environment()
runtime.start(env)
```

**Output:**
```
Starting calculation
Result: 30
Calculation complete
```

## The Environment Class

The `Environment` class manages variables, state, and execution context for commands.

### Creating an Environment

```python
import arrowbit

# Non-strict mode (default) - variables can be assigned without declaration
env = arrowbit.Environment(strict=False)

# Strict mode - variables must be declared before assignment
env_strict = arrowbit.Environment(strict=True)
```

**Parameters:**
- `strict` (bool): If `True`, variables must be declared before assignment. Default: `False`

### Working with Variables

#### Declaring Variables (Strict Mode)

In strict mode, declare variables before using them:

```python
env = arrowbit.Environment(strict=True)

# Declare a variable
env.declare('username')

# Now you can assign it
env.assign('username', arrowbit.Object('STR', 'Alice'))
```

#### Assigning Variables

```python
env = arrowbit.Environment()

# Assign a string variable
env.assign('name', arrowbit.Object('STR', 'Bob'))

# Assign an integer variable
env.assign('age', arrowbit.Object('INT', 25))

# Assign a boolean variable
env.assign('active', arrowbit.Object('BOOL', True))

# Assign a list variable
env.assign('items', arrowbit.Object('LIST', [1, 2, 3]))
```

#### Reading Variables

```python
# Check if variable exists
if 'name' in env.variables:
    # Access the variable
    name_obj = env.variables['name']
    print(name_obj.value)  # 'Bob'
    print(name_obj.type)   # 'STR'
```

#### Deleting Variables

```python
env.delete('name')  # Removes the variable
```

### Read-Only Context

The environment provides read-only context data, particularly for context flags:

```python
@arrowbit.command(name='test')
def test_command(env: arrowbit.Environment):
    # Access context flags
    ctx_flags = env.readonly['ctx'].value
    
    if 'verbose' in ctx_flags:
        print("Verbose mode enabled")
    
    if 'debug' in ctx_flags:
        print("Debug mode enabled")

# Usage with context flags
repl.execute('test @verbose @debug')
```

### Exporting Results

Commands can export results using `env.export()`:

```python
@arrowbit.command(name='calculate')
def calculate(env: arrowbit.Environment, x: int, y: int):
    result = x + y
    env.export(arrowbit.Object('INT', result))

# The exported value is stored in env.result
```

### Inheriting Environments

Create a new environment that inherits from another:

```python
parent_env = arrowbit.Environment(strict=True)
parent_env.assign('global_var', arrowbit.Object('STR', 'shared'))

child_env = arrowbit.Environment()
child_env.herit(parent_env)

# child_env now has 'global_var' and is in strict mode
```

## Direct Execution with REPL

For quick, single-command execution, use the `repl` module:

```python
from arrowbit import repl

# Execute a single command
result = repl.execute('mycommand "arg1" "arg2"')

# Execute with strict mode
result = repl.execute('mycommand "arg1"', strict=True)
```

**Parameters:**
- `cmd` (str or Command): The command to execute
- `strict` (bool): Enable strict mode for variable assignment. Default: `True`

**Returns:**
- The exported result from the command (if any)

## Execution Flow

### Simple Execution Flow

```
1. Load script/command
2. Parse command
3. Resolve variables and parameters
4. Execute command function
5. Export result (if any)
```

### Full Runtime Flow

```
1. Create Runtime and Environment
2. Load script with runtime.load()
3. Call runtime.start()
   ├─ Trigger on_start() handler (if main=True)
   ├─ Iterate through each command
   │  ├─ Parse command
   │  ├─ Process context flags
   │  ├─ Resolve variables
   │  ├─ Execute command
   │  └─ Handle errors (if any)
   └─ Trigger on_exit() handler (if main=True)
```

## Cycling Execution

The runtime supports cycling through commands repeatedly:

```python
runtime = arrowbit.Runtime()
runtime.is_cycle = True  # Enable cycling

runtime.load("""
say "Iteration"
""")

runtime.start()  # Will loop forever (until interrupted)
```

**Note:** The current cycle number is stored in `runtime.cycle`

## Event Handlers

Define handlers for runtime events:

### On Start

Executed when the runtime starts (only if `main=True`):

```python
@arrowbit.on_start()
def startup(env: arrowbit.Environment):
    print("Application starting...")
    env.assign('start_time', arrowbit.Object('INT', time.time()))
```

### On Error

Executed when an error occurs:

```python
@arrowbit.on_error()
def error_handler(env: arrowbit.Environment, err: arrowbit.errors.Error):
    print(f"Error Type: {err.title}")
    print(f"Message: {err.message}")
    
    # Handle specific errors
    if isinstance(err, arrowbit.errors.UserCancel):
        print("User cancelled the operation")
    elif isinstance(err, arrowbit.errors.UnknownName):
        print("Variable or command not found")
```

### On Exit

Executed when the runtime exits normally (only if `main=True`):

```python
@arrowbit.on_exit()
def cleanup(env: arrowbit.Environment):
    print("Cleaning up...")
    
    # Save state
    if 'data' in env.variables:
        save_to_file(env.variables['data'].value)
    
    print("Application closed")
```

## Advanced Examples

### Custom Command Runner

```python
import arrowbit

class CommandRunner:
    def __init__(self):
        self.runtime = arrowbit.Runtime(main=False)
        self.env = arrowbit.Environment(strict=False)
    
    def run_script(self, script: str):
        self.runtime.load(script)
        self.runtime.start(self.env)
    
    def get_variable(self, name: str):
        if name in self.env.variables:
            return self.env.variables[name].value
        return None
    
    def set_variable(self, name: str, value, type_name: str = 'STR'):
        self.env.assign(name, arrowbit.Object(type_name, value))

# Usage
runner = CommandRunner()
runner.set_variable('greeting', 'Hello, World!')
runner.run_script('say $greeting')
```

### Interactive Command Loop

```python
import arrowbit
from arrowbit import repl

@arrowbit.command(name='exit')
def exit_command(env: arrowbit.Environment):
    print("Goodbye!")
    raise SystemExit

@arrowbit.command(name='help')
def help_command(env: arrowbit.Environment):
    print("Available commands: help, echo, exit")

@arrowbit.command(name='echo')
def echo_command(env: arrowbit.Environment, message: str):
    print(message)

@arrowbit.on_start()
def welcome(env: arrowbit.Environment):
    print("Welcome! Type 'help' for commands.")

# Start the REPL
repl.run()
```

### Variable Scoping

```python
import arrowbit

@arrowbit.command(name='create_scope')
def create_scope(env: arrowbit.Environment, script: str):
    # Create a new environment that inherits from parent
    scoped_env = arrowbit.Environment()
    scoped_env.herit(env)
    
    # Execute script in scoped environment
    scoped_runtime = arrowbit.Runtime(main=False)
    scoped_runtime.execute(script, scoped_env)
    
    # Changes in scoped_env don't affect parent env
    print("Scope completed")
```

## Best Practices

1. **Use strict mode for larger projects** - Helps catch typos and undefined variables
2. **Create separate environments for isolated execution** - Prevents variable conflicts
3. **Handle errors gracefully** - Always define an `@on_error()` handler
4. **Clean up in `@on_exit()`** - Save state, close files, release resources
5. **Export results explicitly** - Use `env.export()` for command return values
6. **Use typed objects** - Always create `Object` instances with proper types
7. **Check variable existence** - Use `if 'name' in env.variables:` before accessing

## Performance Tips

- Reuse Runtime and Environment instances when possible
- Avoid excessive variable creation in loops
- Use direct execution (`repl.execute()`) for single commands
- Cache parsed commands when executing repeatedly

## Troubleshooting

### "Name is not defined" Error

```python
# Problem: Variable not declared in strict mode
env = arrowbit.Environment(strict=True)
env.assign('x', arrowbit.Object('INT', 5))  # Error!

# Solution: Declare first
env.declare('x')
env.assign('x', arrowbit.Object('INT', 5))  # OK
```

### Commands Not Found

```python
# Problem: Command defined after execution attempt
repl.execute('mycommand')  # Error: UnknownName

@arrowbit.command(name='mycommand')
def mycommand(env):
    pass

# Solution: Define commands before execution
@arrowbit.command(name='mycommand')
def mycommand(env):
    pass

repl.execute('mycommand')  # OK
```

### Environment Not Persisting

```python
# Problem: Creating new environment each time
def run_command(cmd):
    env = arrowbit.Environment()  # New environment!
    repl.execute(cmd)

# Solution: Reuse environment
env = arrowbit.Environment()

def run_command(cmd):
    repl.execute(cmd)  # Uses default env
```
