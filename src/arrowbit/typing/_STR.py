from ..ext.parser import Object
from functools import total_ordering

@total_ordering
class STRING(Object):
    def __init__(self, value: str = ""):
        super().__init__('STR', str(value))

    def _coerce(self, other):
        if isinstance(other, STRING):
            return other.value

        if isinstance(other, str):
            return other

        return NotImplemented

    def __str__(self):
        return self.value

    def __eq__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return self.value == other_val

    def __lt__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return self.value < other_val

    def __add__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return STRING(self.value + other_val)

    def __radd__(self, other):
        return self.__add__(other)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, key):
        return STRING(self.value[key])

    def __contains__(self, item):
        item_val = self._coerce(item)

        if item_val is NotImplemented:
            return False

        return item_val in self.value

    def __hash__(self):
        return hash(self.value)