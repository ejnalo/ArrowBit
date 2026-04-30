import time
from typing import Any

from . import errors
from .core import x_tokens


class Object:
	def __init__(self, _type: str, value: str = 'null', script: bool = False):
		self.id = hex(round(time.time()))[2:].upper()
		self.type = _type
		self.value: Any = value

		self.script: bool = script

	def copy(self) -> Object:
		o = Object(self.type, self.value)
		return o

	def __repr__(self, deep: int = 0):
		if self.type in ('STR', 'PATH'):
			return (deep * '\t') + f"<{self.type}['{self.value}']>"
		elif self.type == 'LIST':
			output = (deep * '\t') + f'<LIST>\n'

			for item in self.value:
				if isinstance(item, Command):
					output += item.__repr__()

				elif item.type in ('LIST', 'DICT'):
					output += item.__repr__(deep + 1)
				else:
					output += (deep + 1) * '\t'
					output += item.__repr__()

				output += '\n'

			output += (deep * '\t') + f'<ENDLIST>'
			return output

		elif self.type == 'DICT':
			return f"<{self.type}[{ ', '.join([ name + '=' + obj.__repr__() for name, obj in self.value.items() ]) }]>"

		else:
			return (deep * '\t') + f"<{self.type}[{self.value}]>"


class Variable:
	def __init__(self, name: str, obj: Object = None):
		self.name = name
		self.obj = obj

	def __repr__(self):
		return f"Variable(name='{self.name}', value=\"{self.obj.value}\", type={self.obj.type})"


class Argument(Variable):
	def __init__(self, name: str, obj: Object, description: str = ""):
		super().__init__(name, obj)
		self.description = description


class Command:
	def __init__(self):
		self.path = '.'
		self.args: list[Object] = []
		self.kwargs: list[Argument] = []
		self.context: list[str] = []
		self.unparsed: str = ""

		# 🔥 NEW: fallback support
		self.fallback: Command | None = None

	def __repr__(self):
		return (
			f"Command(path={self.path}, "
			f"args={[obj.type + '[' + str(obj.value) + ']' for obj in self.args]}, "
			f"kwargs={[arg.name + ':' + arg.obj.type + '=' + str(arg.obj.value) for arg in self.kwargs]}, "
			f"context={self.context}, "
			f"unparsed={self.unparsed})"
		)


# -----------------------------
# VALUE PARSING (UNCHANGED)
# -----------------------------

def parse_val(entry: str) -> Object:
	if (entry.startswith('"') and entry.endswith('"')) or (entry.startswith("'") and entry.endswith("'")):
		return Object('STR', entry[1:-1])

	elif (entry.startswith('{') and entry.endswith('}')):
		script_lines = parse_script(entry[1:-1])
		commands = [ parse_cmd(line) for line in script_lines ]

		return Object('LIST', commands, script = True)

	elif (entry.startswith('<') and entry.endswith('>')):
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

		if current.strip():
			items.append(current.strip())

		obj = Object('LIST', [])
		for item in items:
			obj.value.append(parse_val(item))

		return obj

	elif entry.isnumeric() and '.' not in entry:
		return Object('INT', int(entry))

	elif entry.isnumeric() and '.' in entry:
		if entry.count('.') > 1:
			raise ValueError("Floating point may not have several dots.")
		return Object('FLOAT', float(entry))

	elif entry.startswith('0x'):
		return Object('INT', int(entry, 16))

	elif entry.startswith('0b'):
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


# -----------------------------
# TOKENIZER (UNCHANGED)
# -----------------------------

def tokenize(literal: str) -> list[str]:
	parts = []
	seq = ""

	ignore = False
	is_comment = False
	string_type = None
	stack = []

	open_to_close = {'[': ']', '(': ')', '{': '}', '<': '>'}
	close_to_open = {']': '[', ')': '(', '}': '{', '>': '<'}

	for idx, c in enumerate(literal):
		next_c = literal[idx + 1] if idx + 1 < len(literal) else ''

		if is_comment:
			if c == '>' and next_c == '>':
				is_comment = False
			continue

		if c == '<' and next_c == '<' and string_type is None and not stack:
			is_comment = True
			continue

		if c == ' ' and not (ignore or string_type or stack):
			if seq:
				parts.append(seq)
				seq = ''
			continue

		if c == '\\':
			ignore = not ignore
			continue

		if c in ('"', "'") and not ignore:
			string_type = None if string_type == c else c if string_type is None else string_type

		if string_type is None:
			if c in open_to_close:
				stack.append(c)
			elif c in close_to_open:
				if not stack or stack[-1] != close_to_open[c]:
					raise errors.InvalidSyntax("Mismatched brackets.")
				stack.pop()

		seq += c

	if string_type or stack:
		raise errors.InvalidSyntax("Mismatched brackets.")

	if seq:
		parts.append(seq)

	return parts


# -----------------------------
# 🔥 NEW: fallback parsing helpers
# -----------------------------

def split_fallback(parts: list[str]) -> list[list[str]]:
	groups = []
	current = []
	stack = []

	for part in parts:
		if part == ':' and not stack:
			groups.append(current)
			current = []
			continue

		for c in part:
			if c in "([{<":
				stack.append(c)
			elif c in ")]}>":
				if stack:
					stack.pop()

		current.append(part)

	if current:
		groups.append(current)

	return groups


def parse_single(parts: list[str]) -> Command:
	context = []
	command = Command()
	command.unparsed = " ".join(parts)

	curr_arg = None

	for part in parts:
		if part == "":
			continue

		if part in x_tokens:
			command.path = x_tokens[part]
			continue

		if part.startswith('--'):
			if curr_arg:
				curr_arg.value = 1
				curr_arg.type = "BOOL"
				command.kwargs.append(curr_arg)
				curr_arg = None
			context.append(part[2:])
			continue

		elif part.startswith('-'):
			if curr_arg:
				if curr_arg.type == "BOOL":
					command.kwargs.append(curr_arg)
					curr_arg = Argument(part[1:], Object('NULL'))
				else:
					raise errors.InvalidSyntax("Argument undefined.")
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


# -----------------------------
# 🔥 MAIN FIX: fallback chain support
# -----------------------------

def parse_cmd(cmd: str) -> Command:
	parts = tokenize(cmd)

	chains = split_fallback(parts)

	def build_chain(groups: list[list[str]]) -> Command:
		head = parse_single(groups[0])
		current = head

		for g in groups[1:]:
			next_cmd = parse_single(g)
			current.fallback = next_cmd
			current = next_cmd

		return head

	return build_chain(chains)


# -----------------------------
# SCRIPT PARSER (UNCHANGED)
# -----------------------------

def parse_script(script: str) -> list[str]:
	script = script.replace('\r', '')
	script = '\n'.join([line.strip() for line in script.split('\n')])

	stack = []
	current = ''
	skip = False
	new_script = []

	for c in script:
		if skip:
			skip = False
			current += c
			continue

		if c in ('"', "'"):
			if stack and stack[-1] == c:
				stack.pop()
			else:
				stack.append(c)

		elif c in '{([<':
			stack.append(c)
		elif c in '})]>':
			if not stack:
				raise errors.InvalidSyntax("Unmatched bracket.")
			stack.pop()

		if c == '\\':
			skip = True

		if c == ';' and not stack:
			new_script.append(current.strip())
			current = ''
			continue

		current += c

	if current.strip():
		new_script.append(current.strip())

	return [line.strip() for line in new_script if line.strip()]