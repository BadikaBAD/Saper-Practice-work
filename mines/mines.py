#########################################
#                                       #
#   HELL STARTS HERE..............      #
#                                       #
#########################################

import datetime
import tkinter
import tkinter.simpledialog
import tkinter.messagebox

from lib import mines


class RecordManager:
    _RECORD_FILE = "records.txt"

    @staticmethod
    def add(name: str, score: str) -> None:
        with open(RecordManager._RECORD_FILE, "a+") as file:
            file.write(f"{name} :: {score}\n")

    @staticmethod
    def read() -> list[str]:
        with open(RecordManager._RECORD_FILE, "r") as file:
            return file.read().strip().split('\n')


class GameTile(tkinter.Button):
    def __init__(self, cell: mines.Cell, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cell = cell


class GameClock:
    def __init__(self, parent: tkinter.Frame):
        self._elapsed_time = 0
        self._parent = parent
        self._job_id = None

    def start(self):
        self._update_time()

    def stop(self):
        if self._job_id:
            self._parent.after_cancel(self._job_id)

    @property
    def elapsed_time(self):
        return str(datetime.timedelta(seconds=self._elapsed_time))

    def _update_time(self):
        self._parent.winfo_toplevel().title(self.elapsed_time)
        self._elapsed_time += 1
        self._job_id = self._parent.after(1000, self._update_time)


class GameFrame(tkinter.Frame):
    def __init__(self, parent: tkinter.Tk, height: int = 10, width: int = 10, mines_n: int = 20):
        super().__init__(parent)

        self._clock = GameClock(self)
        self._clock.start()
        self._minefield = mines.Minefield(height, width, mines_n)
        self._tiles = [GameTile(self._minefield.at(x, y)) for x, y in self._minefield]
        self._restart = False
        self._load_images()
        self._init_ui()

    def _init_ui(self):
        menu = tkinter.Menu()
        menu.add_command(label='Records', command=self._show_records)
        menu.add_command(label='Restart', command=self._restart_act)
        self.master.configure(menu=menu)

        for x, y in self._minefield:
            cell = self._minefield.at(x, y)

            _2_to_1 = x + self._minefield.height * y

            self._tiles[_2_to_1].bind("<Button-1>", lambda _, x_=x, y_=y: self._open(x_, y_))
            self._tiles[_2_to_1].bind("<Button-3>", lambda _, x_=x, y_=y: self._flag(x_, y_))
            self._tiles[_2_to_1].grid(row=y, column=x)

        self._refresh()

    def _show_records(self):
        tkinter.messagebox.showinfo("RECORDS", '\n'.join(RecordManager.read()))

    def _load_images(self):
        self._tile_close = tkinter.PhotoImage(file="img/tile_close.png")
        self._tile_bomb = tkinter.PhotoImage(file="img/tile_bomb.png")
        self._tile_explode = tkinter.PhotoImage(file="img/tile_explode.png")
        self._tile_miss = tkinter.PhotoImage(file="img/tile_miss.png")
        self._tile_flag = tkinter.PhotoImage(file="img/tile_flag.png")
        self._tile_n = [tkinter.PhotoImage(file=f"img/tile_{i}.png") for i in range(9)]

    def _get_image_by_cell(self, cell: mines.Cell) -> tkinter.PhotoImage:
        image = None
        if self._minefield.exploded:
            if cell.opened:
                image = self._tile_bomb if cell.mined else self._tile_n[cell.mines_around]
            elif cell.flagged:
                image = self._tile_flag if cell.mined else self._tile_miss
            else:
                image = self._tile_explode if cell.mined else self._tile_close
        else:
            if cell.opened:
                image = self._tile_n[cell.mines_around]
            elif cell.flagged:
                image = self._tile_flag
            else:
                image = self._tile_close

        return image

    def _refresh(self) -> None:
        for x, y in self._minefield:
            cell = self._minefield.at(x, y)

            _2_to_1 = x + self._minefield.height * y

            self._tiles[_2_to_1].cell = cell
            self._tiles[_2_to_1].configure(image=self._get_image_by_cell(cell))
        self.update()

    @staticmethod
    def _refresh_wrap(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            args[0]._refresh()
        return wrapper

    @staticmethod
    def _check_state(func):
        def wrapper(*args, **kwargs):
            obj = args[0]

            func(*args, **kwargs)

            if obj._minefield.exploded or obj._minefield.is_win():
                obj._clock.stop()
                for tile in obj._tiles:
                    tile.unbind("<Button-1>")
                    tile.unbind("<Button-3>")

            if obj._minefield.exploded:
                NotifyManager.loose()
                obj._restart_act()

            if obj._minefield.is_win():
                NotifyManager.win(obj)
                obj._restart_act()

        return wrapper

    def _restart_act(self):
        self._restart = True
        self.master.destroy()

    @_check_state
    @_refresh_wrap
    def _open(self, x: int, y: int) -> None:
        self._minefield.open(x, y)

    @_check_state
    @_refresh_wrap
    def _flag(self, x: int, y: int) -> None:
        self._minefield.flag(x, y)

    @property
    def clock(self) -> GameClock:
        return self._clock

    @property
    def restart(self):
        return self._restart


class NotifyManager:
    @staticmethod
    def win(game: GameFrame):
        name = tkinter.simpledialog.askstring("you win", "what's your name?")
        if name:
            RecordManager.add(name, game.clock.elapsed_time)

    @staticmethod
    def loose():
        tkinter.messagebox.showinfo("you loose", "KA-BOOM!!!")


def main() -> None:
    while True:
        game = GameFrame(tkinter.Tk())
        game.mainloop()

        if not game.restart:
            break


if __name__ == '__main__':
    main()
