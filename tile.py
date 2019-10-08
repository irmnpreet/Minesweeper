from typing import Optional, Any

class Tile:
    def __init__(self, game: Any, x: int, y: int) -> None:
        self.game = game
        self.x_coord = x
        self.y_coord = y
        self._revealed = False
        self._mine = False
        self._flag = False

    def is_revealed(self) -> bool:
        return self._revealed

    def has_mine(self) -> bool:
        return self._mine

    def has_flag(self) -> bool:
        return self._flag

    def adjacent_mine_count(self) -> int:
        return self.game.adjacent_mine_count(self.x_coord,
                                             self.y_coord)

    def has_adjacent_mines(self) -> bool:
        return self.adjacent_mine_count() > 0

    def color(self) -> str:
        if self.is_revealed():
            if self.has_mine():
                return 'red'
            if self.has_adjacent_mines():
                return 'orange'
            return 'lightgreen'
        if self.has_flag():
            return 'purple'
        return 'lightblue'

    def text(self) -> Optional[str]:
        if not self.has_mine() and self.is_revealed():
            if self.has_adjacent_mines():
                return str(self.adjacent_mine_count())
        # otherwise return None, which will prevent
        # any text from being shown on this tile
        return None

    def can_toggle_flag(self) -> bool:
        if self.has_flag():
            return True
        old_color = self.color()
        self._flag = True
        new_color = self.color()
        self._flag = False
        if old_color == new_color:
            return False
        return True

    def change_into_mine(self) -> None:
        self._mine = True

    def set_flag(self) -> None:
        if self.has_flag():
            return
        if not self.can_toggle_flag():
            return
        self._flag = True

    def unset_flag(self) -> None:
        if not self.has_flag():
            return
        if not self.can_toggle_flag():
            return
        self._flag = False

    def reveal(self) -> None:
        if not self.has_flag():
            self._revealed = True

    def __repr__(self) -> str:
        return (f'<Tile revealed={self.is_revealed()} '
                + f'mine={self.has_mine()} '
                + f'flag={self.has_flag()}>')
