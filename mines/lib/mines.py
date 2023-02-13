import ctypes


_LIB = ctypes.CDLL('./lib/libmines.dll')
_init_minefield = _LIB.init_minefield
_free_minefield = _LIB.free_minefield
_open = _LIB.open
_flag = _LIB.flag
_is_win = _LIB.is_win
_is_win.restype = ctypes.c_bool


class Cell(ctypes.Structure):
    _fields_ = [('_mined', ctypes.c_bool),
                ('_opened', ctypes.c_bool),
                ('_flagged', ctypes.c_bool),
                ('_mines_around', ctypes.c_int)]

    @property
    def mined(self) -> bool:
        return self._mined

    @property
    def opened(self) -> bool:
        return self._opened

    @property
    def flagged(self) -> bool:
        return self._flagged

    @property
    def mines_around(self) -> int:
        return self._mines_around


class Minefield(ctypes.Structure):
    _fields_ = [('_width', ctypes.c_int),
                ('_height', ctypes.c_int),
                ('_cells', ctypes.POINTER(ctypes.POINTER(Cell))),
                ('_mines_n', ctypes.c_int),
                ('_opened_n', ctypes.c_int),
                ('_flagged_n', ctypes.c_int),
                ('_exploded', ctypes.c_bool)]

    def __init__(self, width: int, height: int, mines_n: int):
        super().__init__()

        _init_minefield(
            ctypes.byref(self),
            width,
            height,
            mines_n
        )

    def __del__(self):
        _free_minefield(ctypes.byref(self))

    def __iter__(self):
        self.x, self.y = -1, 0
        return self

    def __next__(self):
        if self.x >= self.width - 1 and self.y >= self.height - 1:
            raise StopIteration

        self.x += 1
        if self.x >= self.width:
            self.y += 1
            self.x = 0

        return self.x, self.y

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def mines_n(self) -> int:
        return self._mines_n

    @property
    def opened_n(self) -> int:
        return self._opened_n

    @property
    def flagged_n(self) -> int:
        return self._flagged_n

    @property
    def exploded(self) -> bool:
        return self._exploded

    def open(self, x: int, y: int) -> None:
        _open(ctypes.byref(self), x, y)

    def flag(self, x: int, y: int) -> None:
        _flag(ctypes.byref(self), x, y)

    def is_win(self) -> bool:
        return _is_win(ctypes.byref(self))

    def at(self, x: int, y: int) -> Cell:
        return self._cells[y][x]
