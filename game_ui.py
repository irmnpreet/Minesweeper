from tkinter import Tk, Canvas, Menu, Event, Widget
from tkinter import messagebox
from typing import List, Any

from hexgrid import HexGrid
from choose_difficulty_ui import ChooseDifficultyUI
from difficulty import Difficulty
from hexgrid_ui_utilities import HexGridUIUtilities

class GameUI:
 
    def __init__(self, difficulty: Difficulty) -> None:
        self.window = Tk() # create application window
        self.window.title('HexSweeper')
        # default width & height
        self.window.geometry(f'{800}x{615}')
        self.canvas = Canvas(self.window, bg='white')
        # fill entire window with canvas
        # "fill='both'" allows the canvas to stretch
        # in both x and y direction
        self.canvas.pack(expand=1, fill='both')

        # initialized with irrelevant values before
        # it is properly initialised in the start_new_game
        # method, which calls .restart_game() with correct size
        # and mine count
        self.hex_grid = HexGrid(2, 1)

        # these instance variables are initialised properly in
        # HexGridUIUtilities.draw_field
        self.apothem: float = 0
        self.hshift: float = 0
        self.start_new_game(difficulty)

        self.ui_elements: List[Widget] = [self.canvas]

        self.canvas.bind('<Button-1>', self.on_click)
        # both <Button-2> and <Button-3> need to be bound for OS X and
        # Linux support (due to Tkinter compatibility issues)
        self.canvas.bind('<Button-2>', self.on_secondary_click)
        self.canvas.bind('<Button-3>', self.on_secondary_click)
        self.window.bind('<Configure>', self.on_window_resize)

        self.init_menubar()

        self.window.mainloop()

    def init_menubar(self) -> None:
       
        menubar = Menu(self.window)

        game_menu = Menu(menubar, tearoff=0)
        game_menu.add_command(
            label='New (Easy)',
            command=lambda: self.start_new_game(Difficulty.EASY))
        game_menu.add_command(
            label='New (Intermediate)',
            command=lambda: self.start_new_game(
                Difficulty.INTERMEDIATE))
        game_menu.add_command(
            label='New (Advanced)',
            command=lambda: self.start_new_game(Difficulty.ADVANCED))
        game_menu.add_command(
            label='New (Custom)',
            command=lambda: self.start_new_game(Difficulty.CUSTOM))
        menubar.add_cascade(label='Game', menu=game_menu)

        # finally add the menubar to the root window
        self.window.config(menu=menubar)

        self.ui_elements += [menubar, game_menu]

    def start_new_game(self, difficulty: Difficulty) -> None:
        if difficulty == Difficulty.EASY:
            self.hex_grid.restart_game(5, 8)
            self.draw_field()
        elif difficulty == Difficulty.INTERMEDIATE:
            self.hex_grid.restart_game(10, 45)
            self.draw_field()
        elif difficulty == Difficulty.ADVANCED:
            self.hex_grid.restart_game(13, 80)
            self.draw_field()
        else: # custom difficulty
            # This call takes care of restarting the game
            # with selected board size and mine count,
            # and also redraws the Game UI after difficulty
            # has been set.
            ChooseDifficultyUI(self)

    @staticmethod
    def border() -> float:
        return 20

    def draw_field(self) -> None:
        HexGridUIUtilities.draw_field(self, self.border())

    @staticmethod
    def show_alert(title: str, msg: str) -> None:
        messagebox.showinfo(title, msg)

    def on_click(self, event: Any) -> None:
        self.hex_grid.primary_click(
            (event.x - self.border() - self.hshift,
             event.y - self.border()),
            self.apothem,
            self.draw_field,
            self.show_alert)

    def on_secondary_click(self, event: Any) -> None:
        self.hex_grid.secondary_click(
            (event.x - self.border() - self.hshift,
             event.y - self.border()),
            self.apothem,
            self.draw_field,
            self.show_alert)

    def on_window_resize(self, _: Event) -> None:
        # recalculates apothem and hshift values automatically
        # for the new window size
        self.draw_field()
