from typing import TYPE_CHECKING, Any

from ..ext.core import command_registry
from ..ext.parser import Object, Command, parse_cmd, parse_script
from ..ext import errors

if TYPE_CHECKING:
    from ..ext.runtime import Environment, Runtime


class ASTNode:
    def __repr__(self, deep: int = 0) -> str:
        raise NotImplementedError

    def eval(self, runtime: Runtime, env: Environment) -> Any:
        raise NotImplementedError

class ValueNode(ASTNode):
    def __init__(self, obj: Object):
        self.obj = obj

    def __repr__(self, deep: int = 0):
        return self.obj.__repr__(deep)

    def eval(self, runtime: Runtime, env: Environment) -> Object:
        return self.obj

class VarNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self, deep: int = 0):
        return deep * "\t" + f"<VARIABLE {self.name}>"

    def eval(self, runtime: Runtime, env: Environment) -> Object:
        try:
            return env.variables[self.name]
        except KeyError:
            var = Object('NULL')
            env.assign(self.name, var)
            return var

class FallbackNode(ASTNode):
    def __init__(self, nodes: list[ASTNode]):
        self.nodes: list[ASTNode] = nodes  # ordered fallback chain

    def __repr__(self, deep: int = 0):
        output = (deep * '\t') + "<FALLBACK>\n"

        for n in self.nodes:
            output += n.__repr__(deep + 1) + "\n"

        return output + (deep * '\t') + "<ENDFALLBACK>"

    def eval(self, runtime: Runtime, env: Environment) -> Any:
        last_error = None

        for node in self.nodes:
            try:
                return node.eval(runtime, env)
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error

class CommandNode(ASTNode):
    def __init__(
        self,
        path: str,
        args: list[ASTNode],
        kwargs: dict[str, ASTNode],
        context: list[str],
    ):
        self.path: str = path
        self.args: list[ASTNode] = args
        self.kwargs: dict[str, ASTNode] = kwargs
        self.context: list[str] = context

    def __repr__(self, deep: int = 0):
        output = (deep * '\t') + f'<COMMAND {self.path}>\n'

        for arg in self.args:
            output += arg.__repr__(deep + 1)
            output += '\n'

        for argname, arg in self.kwargs.items():
            output += arg.__repr__(deep + 1)
            output += '\n'

        if self.context:
            output += (deep + 1) * '\t'
            output += "<CMDCONTEXT>\n"

            for ctx in self.context:
                output += (deep + 2) * '\t'
                output += ctx
                output += '\n'

            output += (deep + 1) * '\t'
            output += "<ENDCMDCONTEXT>\n"

        return output + (deep * '\t') + '<ENDCOMMAND>'

    def eval(self, runtime: Runtime, env: Environment) -> Any:
        # apply context
        for flag in self.context:
            env.readonly['ctx'].value.append(flag)

        # evaluate args
        evaluated_args = [arg.eval(runtime, env).value for arg in self.args]

        evaluated_kwargs = {
            k: v.eval(runtime, env).value
            for k, v in self.kwargs.items()
        }

        func = command_registry.get(self.path)
        if not func:
            raise errors.UnknownName(self.path)

        callback = func["function"]
        sig = func["signature"]

        try:
            sig.bind(env, *evaluated_args, **evaluated_kwargs)
        except TypeError as e:
            msg = str(e)
            if "missing" in msg:
                raise errors.MissingArgument(self.path) from e
            elif "unexpected" in msg or "too many" in msg:
                raise errors.TooManyArguments(self.path) from e

        return callback(env, *evaluated_args, **evaluated_kwargs)

class ForLoopNode(ASTNode):
    def __init__(self, statements: list[ASTNode], iterable: ASTNode, varname: str):
        self.statements: list[ASTNode] = statements
        self.iterable: ASTNode = iterable
        self.varname: str = varname

    def __repr__(self, deep: int = 0):
        output = (deep * '\t') + '<FORLOOP>\n'

        for stmt in self.statements:
            output += stmt.__repr__(deep + 1)
            output += '\n'

        return output + (deep * '\t') + '<ENDFORLOOP>'

    def eval(self, runtime: Runtime, env: Environment) -> None:
        localenv = env.copy()
        localenv.variables[self.varname] = None
        iterable = self.iterable.eval(runtime, env).value

        for item in iterable:
            localenv.variables[self.varname] = item

            for stmt in self.statements:
                runtime.run_node(stmt, localenv)

class WhileLoopNode(ASTNode):
    def __init__(self, statements: list[ASTNode], condition: ASTNode):
        self.statements: list[ASTNode] = statements
        self.condition: ASTNode = condition

    def __repr__(self, deep: int = 0):
        output = (deep * '\t') + '<WHILELOOP>\n'

        for stmt in self.statements:
            output += stmt.__repr__(deep + 1)
            output += '\n'

        return output + (deep * '\t') + '<ENDWHILELOOP>'

    def eval(self, runtime: Runtime, env: Environment) -> None:
        localenv = env.copy()
        condition = self.condition.eval(runtime, env).value

        while condition:
            for stmt in self.statements:
                runtime.run_node(stmt, localenv)

            condition = self.condition.eval(runtime, env).value

class ScriptNode(ASTNode):
    def __init__(self, statements: list[ASTNode]):
        self.statements: list[ASTNode] = statements

    def __repr__(self, deep: int = 0):
        output = (deep * '\t') + '<SCRIPT>\n'

        for stmt in self.statements:
            output += stmt.__repr__(deep + 1)
            output += '\n'

        return output + (deep * '\t') + '<ENDSCRIPT>'

    def eval(self, runtime: Runtime, env: Environment) -> None:
        last = None

        for stmt in self.statements:
            last = runtime.run_node(stmt, env)

        if last is None:
            if getattr(env, 'result', None) is not None:
                return env.result

            return Object('NULL')

        return last

def build_ast_command(cmd: Command) -> ASTNode:
    def convert(obj: Object) -> ASTNode:
        if obj.type == 'VAR':
            return VarNode(obj.value)

        elif obj.type == 'CMD':
            inner = parse_cmd(obj.value.unparsed)

            if inner.path == 'for':
                if len(inner.args) != 3:
                    raise errors.InvalidSyntax("Invalid for loop syntax")

                varname = inner.args[0].value
                iterable = convert(inner.args[1])
                statements = [build_ast_command(c) for c in inner.args[2].value]

                return ForLoopNode(statements, iterable, varname)

            elif inner.path == 'while':
                if len(inner.args) != 2:
                    raise errors.InvalidSyntax("Invalid while loop syntax")

                condition = convert(inner.args[0])
                statements = [build_ast_command(c) for c in inner.args[1].value]

                return WhileLoopNode(statements, condition)

            return build_ast_command(inner)

        elif obj.type == 'LIST':
            if obj.script:
                return ScriptNode([
                    build_ast_command(c) for c in obj.value
                ])
            else:
                return ValueNode(obj)

        else:
            return ValueNode(obj)

    def build_chain(c: Command) -> ASTNode:
        if c.path == 'for':
            if len(c.args) != 3:
                raise errors.InvalidSyntax("Invalid for loop syntax")

            varname = c.args[0].value
            iterable = convert(c.args[1])
            statements = [build_ast_command(cmd) for cmd in c.args[2].value]

            return ForLoopNode(statements, iterable, varname)

        elif c.path == 'while':
            if len(c.args) != 2:
                raise errors.InvalidSyntax("Invalid while loop syntax")

            condition = convert(c.args[0])
            statements = [build_ast_command(cmd) for cmd in c.args[1].value]

            return WhileLoopNode(statements, condition)

        nodes: list[ASTNode] = []

        current = c
        while current:
            nodes.append(_build_single(current))
            current = current.fallback

        return FallbackNode(nodes) if len(nodes) > 1 else nodes[0]

    def _build_single(cmd: Command) -> CommandNode:
        args: list[ASTNode] = [convert(obj) for obj in cmd.args]

        kwargs: dict[str, ASTNode] = {
            arg.name: convert(arg.obj)
            for arg in cmd.kwargs
        }

        return CommandNode(
            path=cmd.path,
            args=args,
            kwargs=kwargs,
            context=cmd.context
        )

    return build_chain(cmd)

def build_ast(source: str) -> ScriptNode:
    lines = parse_script(source)
    nodes: list[ASTNode] = []

    for line in lines:
        cmd = parse_cmd(line.strip())
        nodes.append(build_ast_command(cmd))

    return ScriptNode(nodes)