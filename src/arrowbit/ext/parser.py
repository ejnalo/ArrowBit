import time
from typing import Any

from . import errors
from .core import x_tokens


class Object:
	def __init__(self, _type: str, value: str = 'null'):
		self.id = hex(round(time.time()))[2:].upper()
		self.type = _type
		self.value: Any = value

	def copy(self) -> Object:
		o = Object(self.type, self.value)

		return o

	def __repr__(self):
		return f"Object(type={self.type}, value=\"{self.value}\")"

class Variable:
	def __init__(self, name: str, obj: Object = None): # = Object('NULL')):
		self.name = name
		self.obj = obj

	def __repr__(self):
		return f"Variable(name='{self.name}', value=\"{self.obj.value}\", type={self.obj.type})"

class Argument(Variable):
	def __init__(self, name: str, obj: Object, description: str = ""):
		super().__init__(name, obj)

		self.description = description

	def __repr__(self):
		return f"Argument(name='{self.name}', value=\"{self.obj.value}\", type={self.obj.type}, description=\"{self.description}\")"

class Command:
	def __init__(self):
		self.path = '.'
		self.args: list[Object] = []
		self.kwargs: list[Argument] = []
		self.context: list[str] = []
		self.unparsed: str = ""

	def __repr__(self):
		return f"Command(path={self.path}, args={[ obj.type + "[" + str(obj.value) + "]" for obj in self.args ]}, kwargs={[ arg.name + ":" + arg.obj.type + "=" + str(arg.obj.value) for arg in self.kwargs ]}, context={self.context}, unparsed={self.unparsed})"

	def get(self, key: str, alt: str = None, strict: bool = False) -> Object:
		for arg in self.kwargs:
			if arg.name == key:
				return arg.obj
		else:
			if alt:
				return alt

			if strict:
				raise ValueError(f"Didn't find {key} in defined arguments.")

	def copy(self) -> Command:
		c = Command()

		c.path = self.path

		for arg in self.kwargs:
			a = Argument(arg.name, arg.obj.copy(), arg.description)
			c.kwargs.append(a)

		for obj in self.args:
			o = obj.copy()
			c.args.append(o)

		c.context = self.context.copy()
		c.unparsed = self.unparsed

		return c

	def map_kwargs(self) -> dict[str, Object]:
		return { arg.name: arg.obj.value for arg in self.kwargs }

	def list_args(self) -> tuple:
		return tuple([ obj.value for obj in self.args ])

def parse_val(entry: str) -> Object:
	if (entry.startswith('"') and entry.endswith('"')) or (entry.startswith("'") and entry.endswith("'")):
		return Object('STR', entry[1:-1])

	elif (entry.startswith('{') and entry.endswith('}')):
		cmd = parse_script(entry[1:-1])

		if len(cmd) == 1:
			return Object('CMD', parse_cmd(cmd[0]))

		return Object('LIST', [ parse_cmd(c) for c in cmd ])

	elif (entry.startswith('<') and entry.endswith('>')): # TODO: Real evaluation, not that dangerouss thing
		condition = entry[1:-1]

		result = eval(condition, {})

		if result is True:
			return Object('BOOL', 'TRUE')
		elif result is False:
			return Object('BOOL', 'FALSE')
		else:
			return Object('INT', result)

	elif (entry.startswith('[') and entry.endswith(']')):
		if entry == '[]':
			return Object('LIST', [])

		items = []
		current = ''
		_is_open = False
		_closes = ''

		_matches = {
			'(': ')',
			"'": "'",
			'"': '"',
			'{': '}',
			'[': ']',
			'<': '>'
		}

		for c in entry[1:-1]:
			if not _is_open and c in _matches.keys():
				_is_open = True
				_closes = _matches[c]

			elif _is_open and c == _closes:
				_is_open = False
				_closes = ''

			if c == ',' and not _is_open:
				items.append(current.strip())
				current = ''
			else:
				current += c

		if current.strip() != '':
			items.append(current.strip())

		obj = Object('LIST', [])

		for item in items:
			obj.value.append(parse_val(item))

		return obj

	elif entry.isnumeric() and '.' not in entry:
		return Object('INT', int(entry))

	elif entry.isnumeric() and '.' in entry:
		if entry.count('.') > 1:
			raise ValueError("Floating point may not have several floats.")

		return Object('FLOAT', float(entry))

	elif entry.startswith('0x'):
		return Object('INT', int(entry, 16))

	elif entry[2:].isnumeric() and entry.startswith('0b'):
		return Object('INT', int(entry, 2))

	elif entry.startswith('$'):
		return Object('VAR', entry[1:])

	elif entry in ('TRUE', 'FALSE'):
		return Object('BOOL', entry == 'TRUE')

	elif entry == 'NULL':
		return Object('NULL')

	elif entry in ('STR', 'INT', 'FLOAT', 'BOOL', 'CMD', 'PATH', 'NULL'):
		return Object('TYPE', entry)

	else:
		return Object('PATH', entry)

def tokenize(literal: str) -> list[str]:
	parts: list[str] = []
	seq: str = ""

	ignore: bool = False
	is_comment: bool = False
	string_type: str = None
	stack: list[str] = []

	open_to_close = {
		'[': ']',
		'(': ')',
		'{': '}',
		'<': '>',
	}

	close_to_open = {
		']': '[',
		')': '(',
		'}': '{',
		'>': '<',
	}

	for idx, c in enumerate(literal):
		next_c = literal[idx + 1] if idx + 1 < len(literal) else ''

		if is_comment:
			if c == '>' and next_c == '>':
				is_comment = False

			continue

		if c == '<' and next_c == '<' and string_type is None and len(stack) == 0:
			is_comment = True
			continue

		if c == ' ' and not (ignore or string_type or stack):
			if seq != "":
				parts.append(seq)
				seq = ""

			continue

		if c == '\\':
			ignore = not ignore
			continue

		if c == '"' and not ignore:
			if string_type == '"':
				string_type = None
			elif string_type is None:
				string_type = '"'

		if c == '\'' and not ignore:
			if string_type == '\'':
				string_type = None
			elif string_type is None:
				string_type = '\''

		if string_type is None:
			if c in open_to_close:
				stack.append(c)
			elif c in close_to_open:
				if len(stack) == 0 or stack[-1] != close_to_open[c]:
					raise errors.InvalidSyntax("Mismatched brackets.")
				stack.pop()

		seq += c

	if string_type is not None or len(stack) > 0:
		raise errors.InvalidSyntax("Mismatched brackets.")

	if seq != "":
		parts.append(seq)

	return parts

def parse_cmd(cmd: str) -> Command:
	context: list[str] = []

	command = Command()
	command.unparsed = cmd

	parts = tokenize(cmd)

	curr_arg = None

	for part in parts:
		if part == "":
			continue

		if part in x_tokens.keys():
			command.path = x_tokens[part]
			continue

		if part[0:2] == '--':
			if curr_arg:
				curr_arg.value = 1
				curr_arg.type = "BOOL"
				command.kwargs.append(curr_arg)

				curr_arg = None

			context.append(part[2:])
			continue

		elif part[0] == '-':
			if curr_arg:
				if curr_arg.type == "BOOL":
					command.kwargs.append(curr_arg)
					curr_arg = Argument(part[1:], Object('NULL'))
				else:
					raise errors.InvalidSyntax(f"Argument {curr_arg.name} was left undefined.")
			else:
				curr_arg = Argument(part[1:], Object('NULL'))

		else:
			val = parse_val(part)

			if val.type == 'PATH' and command.path == '.':
				command.path = part
			else:
				if curr_arg:
					curr_arg.obj = val
					command.kwargs.append(curr_arg)
				else:
					command.args.append(val)

				curr_arg = None

	command.context = context
	return command

def parse_script(script: str) -> list[str]:
	script = script.replace('\r', '')
	script = '\n'.join([ line.strip() for line in script.split('\n') ])

	line = 1
	column = 1

	stack = []
	current = ''
	skip = False

	new_script = []

	for c in script:
		if c == '\n':
			line += 1
			column = 1
			current += ' '
			continue

		if skip:
			skip = False
			current += c
			column += 1
			continue

		if c in ('"', "'"):
			if len(stack) > 0 and stack[-1] == c:
				stack.pop()
			else:
				stack.append(c)

		elif c in ('{', '(', '[', '<'):
			stack.append(c)

		elif c in ('}', ')', ']', '>'):
			if len(stack) == 0:
				raise errors.InvalidSyntax(c, line, column)

			opening = stack.pop()

			if (c == '}' and opening != '{') or (c == ')' and opening != '(') or (c == ']' and opening != '[') or (c == '>' and opening != '<'):
				raise errors.InvalidSyntax("Mismatched brackets in script.")

		if c == '\\':
			skip = True

		if c == ';' and len(stack) == 0:
			new_script.append(current.strip())
			current = ''
			continue

		current += c
		column += 1

	if current.strip():
		new_script.append(current.strip())

	new_script = [ line.strip() for line in new_script if line.strip() != '' ]

	return new_script