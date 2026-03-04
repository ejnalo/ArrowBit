from functools import wraps
from inspect import signature

from .core import command_registry
from .parser import Object, parse_val

def define_command(name: str):
	def decorator(func):
		sig = signature(func)

		command_registry[name] = {
			"function": func,
			"signature": sig,
		}

		@wraps(func)
		def wrapper(*args, **kwargs):
			returns = func(*args, **kwargs)

			if isinstance(returns, Object):
				return returns
			elif returns is None:
				return Object('NULL')
			else:
				try:
					return parse_val(str(returns))
				except:
					return Object('STR', str(returns))

		return wrapper

	return decorator

command = define_command