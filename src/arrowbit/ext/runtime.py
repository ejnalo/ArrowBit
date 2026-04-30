from ..utils.ast import build_ast, ScriptNode
from .commands import command
from .core import command_registry
from .parser import Object
from . import errors


def on_error():
	return command(name = 'on_error')

def on_start():
	return command(name = 'on_start')

def on_exit():
	return command(name = 'on_exit')

class Environment:
	def __init__(self, strict: bool = False):
		self.variables: dict[str, Object] = {}
		self.readonly: dict[str, Object] = {
			'ctx': Object('LIST', [])
		}
		self.strict: bool = strict # Must or not declare variables before assignment

		self.result: Object = None

	def herit(self, env: Environment):
		self.strict = env.strict

		for var in env.variables.items():
			self.assign(*var)

	def declare(self, name: str):
		self.variables[name] = None

	def assign(self, name: str, obj: Object):
		if name in self.variables.keys() or not self.strict:
			self.variables[name] = obj
		else:
			raise errors.UnknownName(name)

	def delete(self, name: str):
		if name in self.variables.keys():
			del self.variables[name]
		else:
			raise errors.UnknownName(name)

	def export(self, value: Object):
		self.result = value

default_env = Environment()


class Runtime:
    def __init__(self, main: bool = True):
        self.__main: bool = main
        self.env: Environment = default_env
        self.running: bool = False
        self.is_cycle: bool = True
        self.cycle: int = 0

        self.ast: ScriptNode = None

    def load(self, source: str):
        self.ast = build_ast(source)

    def run_node(self, node, env):
        return node.eval(self, env)

    def start(self, env: Environment = None):
        if self.running:
            raise RuntimeError("Runtime already running")

        if env:
            self.env = env

        self.running = True

        try:
            if self.__main and 'on_start' in command_registry:
                command_registry['on_start']["function"](self.env)

            while True:
                self.ast.eval(self, self.env)

                if not self.is_cycle:
                    break

                self.cycle += 1

            self.running = False

        except KeyboardInterrupt:
            if self.__main and 'on_error' in command_registry:
                return command_registry['on_error']["function"](
                    self.env,
                    errors.UserCancel()
                )

            raise

        except errors.Error as e:
            if self.__main and 'on_error' in command_registry:
                return command_registry['on_error']["function"](self.env, e)

            raise

        finally:
            if self.__main and 'on_exit' in command_registry:
                command_registry['on_exit']["function"](self.env)