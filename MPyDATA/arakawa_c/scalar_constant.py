from .impl.field import Field
from .impl.scalar_constant import make_scalar_constant


class ScalarConstant(Field):
    def __init__(self, value):
        super().__init__(0)
        self._impl = make_scalar_constant(value)

    @property
    def value(self):
        return self._impl.value

    def clone(self):
        return ScalarConstant(
            value=self._impl.value
        )