from ..ext.parser import Object

class BOOLEAN(Object):
    def __init__(self, value: bool = False):
        super().__init__('BOOL', bool(value))

    def _coerce(self, other):
        if isinstance(other, BOOLEAN):
            return other.value

        if isinstance(other, bool):
            return other

        return NotImplemented

    def __str__(self):
        return "true" if self.value else "false"

    def __bool__(self):
        return self.value

    def __eq__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return self.value == other_val

    # logical ops (instead of arithmetic)
    def __and__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return BOOLEAN(self.value and other_val)

    def __or__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return BOOLEAN(self.value or other_val)

    def __invert__(self):
        return BOOLEAN(not self.value)

    def __hash__(self):
        return hash(self.value)