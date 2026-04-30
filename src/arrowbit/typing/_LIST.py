from ._ARRAY import ARRAY

class LIST(ARRAY):
    def __init__(self, value = None):
        super().__init__('LIST', list(value) if value is not None else [])