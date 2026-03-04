from inspect import Signature

from .core import command_registry
from .parser import Object, Command, parse_cmd, parse_val, tokenize
from .commands import command
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

		self.env = default_env
		self.running: bool = False
		self.is_cycle: bool = True

		self.__iteration = 0
		self.queue: list[Command] = []
		self.cycle: int = 0

	def load(self, file: str):
		self.queue.clear()

		for line in file.split('\n'):
			cmd = parse_cmd(line.strip())
			self.queue.append(cmd)

	def start(self, env: Environment = None):
		if self.running: raise RuntimeError('Runtime already running')

		if env: self.env = env

		if self.__main and 'on_start' in command_registry:
			cmd = command_registry['on_start']
			_on_start = cmd["function"]
			_on_start(self.env)

		self.__iteration = 0
		self.running = True

		try:
			while self.__iteration < len(self.queue):
				line = self.queue[self.__iteration]
				self.execute(line.unparsed)

				self.__iteration += 1

				if self.__iteration >= len(self.queue):
					if self.is_cycle:
						self.__iteration = 0
						self.cycle += 1

		except KeyboardInterrupt as e:
			if self.__main and 'on_error' in command_registry:
				cmd = command_registry['on_error']
				_on_error = cmd["function"]
				return _on_error(env, errors.UserCancel())
			else:
				raise e
		except SystemExit:
			pass

		if self.__main and 'on_exit' in command_registry:
			cmd = command_registry['on_exit']
			_on_exit = cmd["function"]
			_on_exit(self.env)


	def _convert_object(self, token: Object, env: Environment = None) -> Object:
		if not env: env = self.env

		if token.type == 'VAR':
			try:
				return env.variables[token.value]
			except KeyError:
				raise errors.UnknownName(token.value)			

		elif token.type == 'CMD':
			tenv = Environment(env.strict)
			self.execute(token.value.unparsed, tenv)
			return tenv.result

		else:
			return token

	def _tokenize_condition(self, entry: str, env: Environment = None) -> str:
		"""
		Turns variables et inputs into raw values (STR, INT, BOOL...)
		"""

		if not env: env = self.env

		tokens: list[str] = tokenize(entry[1:-1])

		for token in tokens:
			token = self._convert_object(parse_val(token)).value

		return '<' + ' '.join(tokens) + '>'


	def execute(self, seq: str, env: Environment = None):
		if not env: env = self.env

		if seq == '' or seq.strip().startswith('#'):
			return

		try:
			cmd = parse_cmd(seq)

			for flag in cmd.context:
				env.readonly['ctx'].value.append(flag)

			for arg in cmd.kwargs:
				if arg.obj.type in ('CMD', 'VAR'):
					arg.obj = self._convert_object(arg.obj)
				elif arg.obj.type == 'CONDITION':
					tokenized = self._tokenize_condition(arg.obj.value)
					arg.obj = parse_val(tokenized)

			args = []

			for obj in cmd.args:
				if obj.type in ('CMD', 'VAR'):
					args.append(self._convert_object(obj))
				elif obj.type == 'CONDITION':
					tokenized = self._tokenize_condition(obj.value)
					args.append(parse_val(tokenized))
				else:
					args.append(obj)


			func = command_registry.get(cmd.path)

			if not func:
				raise errors.UnknownName(cmd.path)

			callback = func["function"]
			sig: Signature = func["signature"]

			bound_args = sig.bind_partial(**cmd.map_kwargs())
			args = tuple([ obj.value for obj in args ])

			try:
				sig.bind(env, *args, **bound_args.kwargs)
			except TypeError as e:
				msg = str(e)

				if "missing" in msg:
					raise errors.MissingArgument(cmd.path) from e
				elif "unexpected" in msg or "too many" in msg:
					raise errors.TooManyArguments(cmd.path) from e

			return callback(env, *args, **bound_args.kwargs)
		except errors.Error as e:
			if self.__main and 'on_error' in command_registry:
				cmd = command_registry['on_error']
				_on_error = cmd["function"]
				return _on_error(env, e)
			else:
				raise e