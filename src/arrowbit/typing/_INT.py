from ..ext.parser import Object
from functools import total_ordering

@total_ordering
class INTEGER(Object):
    def __init__(self, value: int = 0):
        super().__init__('INT', int(value))

    def _coerce(self, other):
        if isinstance(other, INTEGER):
            return other.value

        if isinstance(other, int):
            return other

        return NotImplemented

    # --- representation ---
    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    # --- comparisons ---
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

    # --- arithmetic ---
    def __add__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(self.value + other_val)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(self.value - other_val)

    def __rsub__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(other_val - self.value)

    def __mul__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(self.value * other_val)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __floordiv__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(self.value // other_val)

    def __rfloordiv__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(other_val // self.value)

    def __mod__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(self.value % other_val)

    def __rmod__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(other_val % self.value)

    def __pow__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(self.value ** other_val)

    def __rpow__(self, other):
        other_val = self._coerce(other)

        if other_val is NotImplemented:
            return NotImplemented

        return INTEGER(other_val ** self.value)

    # --- unary ---
    def __neg__(self):
        return INTEGER(-self.value)

    def __pos__(self):
        return INTEGER(+self.value)

    def __abs__(self):
        return INTEGER(abs(self.value))

    # --- hashing (important if used as dict keys) ---
    def __hash__(self):
        return hash(self.value)