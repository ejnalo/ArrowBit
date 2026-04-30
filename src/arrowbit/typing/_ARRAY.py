from ..ext.parser import Object

class ARRAY(Object):
    def __init__(self, value=None):
        super().__init__('ARRAY', list(value) if value is not None else [])

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self):
        return str(self.value)

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __contains__(self, item):
        return item in self.value

    def __getitem__(self, index):
        result = self.value[index]

        if isinstance(index, slice):
            return self.__class__(result)

        return result

    def __setitem__(self, index, value):
        self.value[index] = value

    def __eq__(self, other):
        if isinstance(other, ARRAY):
            return self.value == other.value

        if isinstance(other, list):
            return self.value == other

        return NotImplemented

    def __add__(self, other):
        if isinstance(other, ARRAY):
            return self.__class__(self.value + other.value)

        if isinstance(other, list):
            return self.__class__(self.value + other)

        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, ARRAY):
            self.value += other.value
            return self

        if isinstance(other, list):
            self.value += other
            return self

        return NotImplemented

    def append(self, item):
        self.value.append(item)

    def extend(self, iterable):
        if isinstance(iterable, ARRAY):
            self.value.extend(iterable.value)
        else:
            self.value.extend(iterable)

    def pop(self, index = -1):
        return self.value.pop(index)

    def copy(self):
        return self.__class__(self.value.copy())

    def __hash__(self):
        try:
            return hash(tuple(self.value))
        except TypeError:
            raise TypeError(f"{self.__class__.__name__} is unhashable because it contains unhashable elements")