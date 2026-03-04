from .commands import command
from .runtime import Environment

class Cog:
    def __init__(self, env: Environment):
        self.name = '__main__'
        self.env = env

    def setup(self):
        raise NotImplementedError("A setup() method must be defined")

    def command(self, name: str):
        if self.name == '__main__':
            return command(name)
        else:
            return command(self.name + '.' + name)

def load_cog(cog: Cog, name: str = '__main__'):
    if not issubclass(type(cog), Cog):
        raise TypeError(f"Expected a Cog object, got {type(Cog).__name__}.")

    cog.name = name
    cog.setup()