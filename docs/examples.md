# Examples and Use Cases

This guide provides practical examples and use cases for ArrowBit, demonstrating how to build real-world applications.

## Table of Contents

1. [Simple Calculator](#simple-calculator)
2. [File Manager](#file-manager)
3. [Task Runner](#task-runner)
4. [Interactive Quiz](#interactive-quiz)
5. [Configuration Manager](#configuration-manager)
6. [Mini Programming Language](#mini-programming-language)
7. [Command-Line Tool](#command-line-tool)

---

## Simple Calculator

A basic calculator with arithmetic operations.

```python
import arrowbit
from arrowbit import cogs, Environment, repl

class CalculatorCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
    
    def setup(self):
        @self.command('add')
        def add(env: Environment, a: float, b: float):
            result = a + b
            print(f"{a} + {b} = {result}")
            env.export(arrowbit.Object('INT', result))
        
        @self.command('subtract')
        def subtract(env: Environment, a: float, b: float):
            result = a - b
            print(f"{a} - {b} = {result}")
            env.export(arrowbit.Object('INT', result))
        
        @self.command('multiply')
        def multiply(env: Environment, a: float, b: float):
            result = a * b
            print(f"{a} × {b} = {result}")
            env.export(arrowbit.Object('INT', result))
        
        @self.command('divide')
        def divide(env: Environment, a: float, b: float):
            if b == 0:
                raise arrowbit.errors.Error("Cannot divide by zero")
            result = a / b
            print(f"{a} ÷ {b} = {result}")
            env.export(arrowbit.Object('INT', result))
        
        @self.command('power')
        def power(env: Environment, base: float, exponent: float):
            result = base ** exponent
            print(f"{base} ^ {exponent} = {result}")
            env.export(arrowbit.Object('INT', result))

# Setup
env = arrowbit.Environment()
cogs.load_cog(CalculatorCog(env), name='calc')

# Usage
repl.execute('calc.add 10 5')        # 10 + 5 = 15
repl.execute('calc.multiply 4 7')    # 4 × 7 = 28
repl.execute('calc.power 2 8')       # 2 ^ 8 = 256
```

---

## File Manager

A simple file management system.

```python
import arrowbit
from arrowbit import cogs, Environment, errors
import os

class FileManagerCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
    
    def setup(self):
        @self.command('read')
        def read_file(env: Environment, filepath: str):
            """Read and display file contents"""
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                print(content)
                env.export(arrowbit.Object('STR', content))
            except FileNotFoundError:
                raise errors.Error(f"File not found: {filepath}")
            except PermissionError:
                raise errors.Error(f"Permission denied: {filepath}")
        
        @self.command('write')
        def write_file(env: Environment, filepath: str, content: str):
            """Write content to a file"""
            try:
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"✓ Written to {filepath}")
            except PermissionError:
                raise errors.Error(f"Permission denied: {filepath}")
        
        @self.command('append')
        def append_file(env: Environment, filepath: str, content: str):
            """Append content to a file"""
            try:
                with open(filepath, 'a') as f:
                    f.write(content)
                print(f"✓ Appended to {filepath}")
            except PermissionError:
                raise errors.Error(f"Permission denied: {filepath}")
        
        @self.command('list')
        def list_dir(env: Environment, dirpath: str = '.'):
            """List files in directory"""
            try:
                files = os.listdir(dirpath)
                for file in files:
                    print(f"  {file}")
                env.export(arrowbit.Object('LIST', files))
            except FileNotFoundError:
                raise errors.Error(f"Directory not found: {dirpath}")
        
        @self.command('exists')
        def file_exists(env: Environment, filepath: str):
            """Check if file exists"""
            exists = os.path.exists(filepath)
            print(f"{'✓' if exists else '✗'} {filepath}")
            env.export(arrowbit.Object('BOOL', exists))
        
        @self.command('delete')
        def delete_file(env: Environment, filepath: str):
            """Delete a file"""
            try:
                os.remove(filepath)
                print(f"✓ Deleted {filepath}")
            except FileNotFoundError:
                raise errors.Error(f"File not found: {filepath}")
            except PermissionError:
                raise errors.Error(f"Permission denied: {filepath}")

# Setup
env = arrowbit.Environment()
cogs.load_cog(FileManagerCog(env), name='file')

# Error handler
@arrowbit.on_error()
def handle_error(env: Environment, err: errors.Error):
    print(f"❌ {err.message}")

# Usage
from arrowbit import repl
repl.execute('file.write "test.txt" "Hello, World!"')
repl.execute('file.read "test.txt"')
repl.execute('file.exists "test.txt"')
repl.execute('file.list "."')
```

---

## Task Runner

A task management and execution system.

```python
import arrowbit
from arrowbit import cogs, Environment, errors
import subprocess
import time

class TaskRunnerCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
        self.tasks = {}
    
    def setup(self):
        @self.command('define')
        def define_task(env: Environment, name: str, command: str):
            """Define a new task"""
            self.tasks[name] = command
            print(f"✓ Task '{name}' defined")
        
        @self.command('run')
        def run_task(env: Environment, name: str):
            """Run a defined task"""
            if name not in self.tasks:
                raise errors.UnknownName(name)
            
            command = self.tasks[name]
            print(f"▶ Running task '{name}': {command}")
            
            start_time = time.time()
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            duration = time.time() - start_time
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠ {result.stderr}")
            
            print(f"✓ Task completed in {duration:.2f}s (exit code: {result.returncode})")
        
        @self.command('list')
        def list_tasks(env: Environment):
            """List all defined tasks"""
            if not self.tasks:
                print("No tasks defined")
            else:
                print("Defined tasks:")
                for name, command in self.tasks.items():
                    print(f"  • {name}: {command}")
        
        @self.command('remove')
        def remove_task(env: Environment, name: str):
            """Remove a task"""
            if name in self.tasks:
                del self.tasks[name]
                print(f"✓ Task '{name}' removed")
            else:
                raise errors.UnknownName(name)

# Setup
env = arrowbit.Environment()
cogs.load_cog(TaskRunnerCog(env), name='task')

# Usage
from arrowbit import repl
repl.execute('task.define "greet" "echo Hello, World!"')
repl.execute('task.define "date" "date"')
repl.execute('task.list')
repl.execute('task.run "greet"')
```

---

## Interactive Quiz

A simple quiz application.

```python
import arrowbit
from arrowbit import cogs, Environment, errors

class QuizCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
        self.questions = []
        self.current_question = 0
        self.score = 0
    
    def setup(self):
        @self.command('add-question')
        def add_question(env: Environment, question: str, answer: str):
            """Add a question to the quiz"""
            self.questions.append({'question': question, 'answer': answer})
            print(f"✓ Question {len(self.questions)} added")
        
        @self.command('start')
        def start_quiz(env: Environment):
            """Start the quiz"""
            self.current_question = 0
            self.score = 0
            print("=== Quiz Started ===")
            print(f"Total questions: {len(self.questions)}\n")
            self._ask_next(env)
        
        @self.command('answer')
        def answer_question(env: Environment, answer: str):
            """Answer the current question"""
            if self.current_question >= len(self.questions):
                print("Quiz already completed!")
                return
            
            correct_answer = self.questions[self.current_question]['answer']
            
            if answer.lower().strip() == correct_answer.lower().strip():
                print("✓ Correct!\n")
                self.score += 1
            else:
                print(f"✗ Incorrect. The answer was: {correct_answer}\n")
            
            self.current_question += 1
            
            if self.current_question < len(self.questions):
                self._ask_next(env)
            else:
                self._finish_quiz()
        
        @self.command('skip')
        def skip_question(env: Environment):
            """Skip the current question"""
            print(f"Skipped.\n")
            self.current_question += 1
            
            if self.current_question < len(self.questions):
                self._ask_next(env)
            else:
                self._finish_quiz()
    
    def _ask_next(self, env: Environment):
        """Helper to ask next question"""
        q = self.questions[self.current_question]
        print(f"Question {self.current_question + 1}/{len(self.questions)}:")
        print(q['question'])
        print("Use: quiz.answer \"your answer\" or quiz.skip")
    
    def _finish_quiz(self):
        """Helper to finish quiz"""
        print("=== Quiz Complete ===")
        percentage = (self.score / len(self.questions)) * 100
        print(f"Score: {self.score}/{len(self.questions)} ({percentage:.1f}%)")

# Setup
env = arrowbit.Environment()
cogs.load_cog(QuizCog(env), name='quiz')

# Create a quiz
from arrowbit import repl
repl.execute('quiz.add-question "What is the capital of France?" "Paris"')
repl.execute('quiz.add-question "What is 2 + 2?" "4"')
repl.execute('quiz.add-question "What color is the sky?" "blue"')
repl.execute('quiz.start')

# Answer questions
repl.execute('quiz.answer "Paris"')
repl.execute('quiz.answer "4"')
repl.execute('quiz.skip')
```

---

## Configuration Manager

A system for managing application configuration.

```python
import arrowbit
from arrowbit import cogs, Environment, errors
import json

class ConfigCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
        self.config = {}
        self.config_file = 'config.json'
    
    def setup(self):
        @self.command('set')
        def set_config(env: Environment, key: str, value: str):
            """Set a configuration value"""
            keys = key.split('.')
            current = self.config
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
            print(f"✓ {key} = {value}")
        
        @self.command('get')
        def get_config(env: Environment, key: str):
            """Get a configuration value"""
            keys = key.split('.')
            current = self.config
            
            try:
                for k in keys:
                    current = current[k]
                print(current)
                env.export(arrowbit.Object('STR', str(current)))
            except KeyError:
                raise errors.UnknownName(key)
        
        @self.command('list')
        def list_config(env: Environment, prefix: str = ''):
            """List configuration values"""
            def print_dict(d, indent=0):
                for key, value in d.items():
                    if isinstance(value, dict):
                        print('  ' * indent + f"{key}:")
                        print_dict(value, indent + 1)
                    else:
                        print('  ' * indent + f"{key}: {value}")
            
            if prefix:
                keys = prefix.split('.')
                current = self.config
                for k in keys:
                    current = current[k]
                print_dict(current)
            else:
                print_dict(self.config)
        
        @self.command('save')
        def save_config(env: Environment, filepath: str = None):
            """Save configuration to file"""
            path = filepath or self.config_file
            try:
                with open(path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                print(f"✓ Configuration saved to {path}")
            except Exception as e:
                raise errors.Error(f"Failed to save: {str(e)}")
        
        @self.command('load')
        def load_config(env: Environment, filepath: str = None):
            """Load configuration from file"""
            path = filepath or self.config_file
            try:
                with open(path, 'r') as f:
                    self.config = json.load(f)
                print(f"✓ Configuration loaded from {path}")
            except FileNotFoundError:
                raise errors.Error(f"File not found: {path}")
            except json.JSONDecodeError:
                raise errors.Error(f"Invalid JSON in {path}")

# Setup
env = arrowbit.Environment()
cogs.load_cog(ConfigCog(env), name='config')

# Usage
from arrowbit import repl
repl.execute('config.set "app.name" "MyApp"')
repl.execute('config.set "app.version" "1.0.0"')
repl.execute('config.set "database.host" "localhost"')
repl.execute('config.set "database.port" "5432"')
repl.execute('config.list')
repl.execute('config.get "app.name"')
repl.execute('config.save "myconfig.json"')
```

---

## Mini Programming Language

A simple interpreted language with variables, conditionals, and loops.

```python
import arrowbit
from arrowbit import cogs, Environment, errors

class LanguageCog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
    
    def setup(self):
        @self.command('var')
        def declare_var(env: Environment, name: str, value: str):
            """Declare a variable"""
            env.assign(name, arrowbit.Object('STR', value))
            
            if 'silent' not in env.readonly['ctx'].value:
                print(f"✓ {name} = {value}")
        
        @self.command('print')
        def print_var(env: Environment, name: str):
            """Print a variable or literal"""
            if name.startswith('$'):
                var_name = name[1:]
                if var_name in env.variables:
                    print(env.variables[var_name].value)
                else:
                    raise errors.UnknownName(var_name)
            else:
                print(name)
        
        @self.command('if')
        def if_statement(env: Environment, condition: str, then_cmd: str):
            """Execute command if condition is true"""
            # Parse condition (simplified)
            if condition.lower() in ['true', '1', 'yes']:
                from arrowbit import repl
                repl.execute(then_cmd)
        
        @self.command('repeat')
        def repeat_command(env: Environment, times: int, command: str):
            """Repeat a command multiple times"""
            from arrowbit import repl
            for i in range(times):
                env.assign('i', arrowbit.Object('INT', i))
                repl.execute(command)
        
        @self.command('add')
        def add_command(env: Environment, result_var: str, a: int, b: int):
            """Add two numbers and store in variable"""
            result = a + b
            env.assign(result_var, arrowbit.Object('INT', result))
            
            if 'silent' not in env.readonly['ctx'].value:
                print(f"{result_var} = {result}")

# Setup
env = arrowbit.Environment()
cogs.load_cog(LanguageCog(env), name='lang')

# Example program
from arrowbit import repl

print("=== Mini Program ===")
repl.execute('lang.var "name" "Alice"')
repl.execute('lang.var "greeting" "Hello"')
repl.execute('lang.print "$greeting"')
repl.execute('lang.print "$name"')
repl.execute('lang.add "sum" 10 5')
repl.execute('lang.print "$sum"')
repl.execute('lang.repeat 3 "lang.print \\"Loop iteration\\""')
```

---

## Command-Line Tool

A complete command-line application with help, version, and multiple commands.

```python
import arrowbit
from arrowbit import cogs, Environment, errors, repl
import sys

class CLICog(cogs.Cog):
    def __init__(self, env: Environment):
        super().__init__(env)
        self.app_name = "MyTool"
        self.version = "1.0.0"
    
    def setup(self):
        @self.command('help')
        def help_command(env: Environment, command: str = ''):
            """Show help information"""
            if command:
                # Show help for specific command
                help_text = {
                    'help': 'Show this help message',
                    'version': 'Show version information',
                    'echo': 'Print a message',
                    'count': 'Count from 1 to N',
                    'exit': 'Exit the application'
                }
                if command in help_text:
                    print(f"{command}: {help_text[command]}")
                else:
                    print(f"Unknown command: {command}")
            else:
                print(f"{self.app_name} - Command Line Tool")
                print(f"\nUsage: <command> [arguments]\n")
                print("Available commands:")
                print("  help [command]  - Show help")
                print("  version         - Show version")
                print("  echo <message>  - Print a message")
                print("  count <n>       - Count from 1 to N")
                print("  exit            - Exit")
        
        @self.command('version')
        def version_command(env: Environment):
            """Show version information"""
            print(f"{self.app_name} v{self.version}")
        
        @self.command('echo')
        def echo_command(env: Environment, message: str):
            """Print a message"""
            print(message)
        
        @self.command('count')
        def count_command(env: Environment, n: int):
            """Count from 1 to N"""
            for i in range(1, n + 1):
                print(i)
        
        @self.command('exit')
        def exit_command(env: Environment):
            """Exit the application"""
            print("Goodbye!")
            raise SystemExit

# Setup
env = arrowbit.Environment()
cogs.load_cog(CLICog(env), name='cli')

@arrowbit.on_start()
def startup(env: Environment):
    print("Welcome! Type 'cli.help' for available commands.\n")

@arrowbit.on_error()
def error_handler(env: Environment, err: errors.Error):
    if isinstance(err, errors.UserCancel):
        print("\n Cancelled by user")
    else:
        print(f"Error: {err.message}")

@arrowbit.on_exit()
def cleanup(env: Environment):
    print("Exiting...")

# Run REPL
if __name__ == '__main__':
    repl.run()
```

---

## Best Practices Demonstrated

These examples demonstrate several best practices:

1. **Error Handling**: Always handle potential errors gracefully
2. **User Feedback**: Provide clear feedback for actions (✓, ✗, etc.)
3. **Modularity**: Use Cogs to organize related commands
4. **Validation**: Check inputs before processing
5. **Help Text**: Provide helpful documentation for users
6. **Context Flags**: Use flags for optional behavior (@silent, @verbose)
7. **Export Values**: Return values for command chaining
8. **Event Handlers**: Use on_start, on_error, on_exit appropriately

## Tips for Building Your Own

1. **Start Simple**: Begin with basic commands and add complexity gradually
2. **Plan Structure**: Organize commands into logical Cogs
3. **Test Early**: Test each command as you build
4. **Document**: Add docstrings and help commands
5. **Handle Errors**: Think about what can go wrong and handle it
6. **Provide Feedback**: Let users know what's happening
7. **Use Types**: Leverage Python's type system for parameters
8. **Think About UX**: Make your DSL intuitive and user-friendly
