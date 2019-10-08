import random
import math
import time
from typing import List, Tuple, Callable, Optional

from tile import Tile

class HexGrid:
   
    def __init__(self, size: int, mine_count: int) -> None:
        self.size = size
        self.start_time = time.time()
        self.mines_have_been_generated = False
        self.__init_game(size, mine_count)

    def __init_game(self, size: int, mine_count: int) -> None:
        max_possible_mine_count = \
            HexGrid.highest_possible_mine_count_for_size(size)

        if mine_count > max_possible_mine_count:
            # as the mine count is controlled by a slider, this
            # exception should *never* be thrown.
            field_tiles = max_possible_mine_count + 1
            message = \
                ('Invalid mine count! The chosen field size '
                 + f'of {size} has {field_tiles} tiles, '
                 + f'but you chose to generate {mine_count} mines. '
                 + 'Note that at least one field must be left '
                 + 'blank for the game to be winnable.')
            raise Exception(message)

        # validation completed successfully, now initialise the HexGrid
        self.size = size
        self.grid: List[List[Tile]] = []
        # save number of seconds since epoch
        self.start_time = time.time()
        self.mine_count = mine_count
        # 0 to 2 * size - 2, explained above
        for field_y in range(self.row_count()):
            cell_count_in_current_row = self.cell_count_in_row(field_y)
            row = []
            for field_x in range(cell_count_in_current_row):
                # As explained in tile.py, all new tiles
                # initially have no mines. Mines are only
                # generated on first click to avoid unfair deaths.
                row.append(Tile(self, field_x, field_y))
            self.grid.append(row)

        self.mines_have_been_generated = False

    def row_count(self) -> int:
        return 2 * self.size - 1

    def cell_count_in_row(self, field_y: int) -> int:
        return self.size + min(field_y, 2 * self.size - 2 - field_y)

    def highest_row_cell_count(self) -> int:
        return 2 * self.size - 1

    @staticmethod
    def highest_possible_mine_count_for_size(size) -> int:
        total_tile_count = 3 * size ** 2 - 3 * size + 1
        return total_tile_count - 1

    def all_valid_coords(self) -> List[Tuple[int, int]]:
        
        coords = []
        for field_y in range(self.row_count()):
            for field_x in range(self.cell_count_in_row(field_y)):
                # double parenthesis needed to make a tuple
                coords.append((field_x, field_y))
        return coords

    def __getitem__(self, pos: Tuple[int, int]) -> Tile:
        (field_x, field_y) = pos
        return self.grid[field_y][field_x]

    def __setitem__(self, pos: Tuple[int, int], item: Tile) -> None:
        (field_x, field_y) = pos
        self.grid[field_y][field_x] = item

    def is_y_valid(self, field_y: int) -> bool:
        return 0 <= field_y < self.row_count()

    def is_x_valid(self, field_x: int, field_y: int) -> bool:
        return 0 <= field_x < self.cell_count_in_row(field_y)

    def is_position_valid(self, field_x: int, field_y: int) -> bool:
        return self.is_y_valid(field_y) and \
            self.is_x_valid(field_x, field_y)

    def adjacent_positions(
            self, field_x: int, field_y: int) -> List[Tuple[int, int]]:

        possible_positions = [
            (field_x, field_y + 1),
            (field_x, field_y - 1),
            (field_x + 1, field_y),
            (field_x - 1, field_y)]

        # these three cases are required for the 'bend' in
        # the x-coordinate lines on the hexagonal grid
        if field_y < self.size - 1: # fields above the center row
            possible_positions.append((field_x + 1, field_y + 1))
            possible_positions.append((field_x - 1, field_y - 1))
        elif field_y == self.size - 1: # fields on the center row
            possible_positions.append((field_x - 1, field_y + 1))
            possible_positions.append((field_x - 1, field_y - 1))
        else: # fields below the center row
            possible_positions.append((field_x + 1, field_y - 1))
            possible_positions.append((field_x - 1, field_y + 1))
        # the exact coordinate offsets can be verified by checking the
        # graph and the coordinates of adjacent tiles.

        # Here, the asterisk is used as the tuple unpacking operator.
        # Filtering possible_positions is required for any edge or
        # corner tiles. 'filter' takes a lambda expression and
        # returns a lazy list. Calling the list conversion function
        # on this lazy list forces the list to be fully evaluated,
        # which is required for many operations including getting
        # the length of a list.
        return list(
            filter(
                lambda pos: self.is_position_valid(*pos),
                possible_positions
            )
        )

    def adjacent_mine_count(self, field_x: int, field_y: int) -> int:
        return len(
            list(
                filter(
                    # lambda only returns true if
                    # there is a mine at position pos
                    lambda pos: self[pos].has_mine(),
                    self.adjacent_positions(field_x, field_y)
                ) # this means that the filter statement returns a
                  # lazy list that contains all adjacent tile
                  # coordinates with mines
            ) # this lazy list is then computed and converted
              # to an eager list before we can get its length,
              # as in the method HexGrid.adjacent_positions above
        ) # and finally its length is calculated
          # this length now describes the number
          # of adjacent mines of a given position


    def total_flag_count(self) -> int:
        """ Total number of flags the user has placed """

        # (A) Get all valid coordinates                         (A)
        # (B) For each coordinate pos:                          (B)
        # (C)   - Get the tile at pos                           (C)
        # (D)   - Is there a flag on this tile?                 (D)
        # (E)   - True = 1, False = 0                           (E)
        # (F) Sum of ones and zeroes is the number flags on map (F)

        return sum(
            #  ~^~
            #   F
            #
            # E      C         D
            #~v~ ~~~~v~~~~ ~~~~v~~~~~
            [int(self[pos].has_flag())
             for pos in self.all_valid_coords()])
#            ~^~        ^~~~~~~~~~~~~~~~~~~~~~~
#             B         A

    def flag_limit_reached(self) -> bool:
        return self.total_flag_count() >= self.mine_count

    def restart_game(
            self,
            size: Optional[int] = None,
            mine_count: Optional[int] = None) -> None:
        if not size:
            size = self.size
        if not mine_count:
            mine_count = self.mine_count
        # reinitialize the object in place by explicitly
        # calling __init_game (just like in __init__)
        self.__init_game(size, mine_count)

    def restart_if_game_is_over(
            self,
            redraw: Callable[[], None],
            show_alert: Callable[[str, str], None]):

        #     checking for game over:
        # (A)   - mines have not yet been generated    -> return  (A)
        # (C)   - all non-mine tiles are revealed      -> win     (B)
        # (D)   - a mine is revealed                   -> lose    (C)
        # (E)   - otherwise                            -> return  (D)

        # A
        if not self.mines_have_been_generated:
            redraw()
            return

        # B
        number_of_safe_hidden_tiles = len(
            [pos for pos in self.all_valid_coords()
             if not self[pos].has_mine()
             and not self[pos].is_revealed()])
        if number_of_safe_hidden_tiles == 0:
            # no safe but hidden tiles -> win (B)
            for pos in self.all_valid_coords():
                if not self[pos].has_flag():
                    self[pos].reveal()
            redraw()
            end_time = time.time()
            mins = (end_time - self.start_time) // 60
            secs = end_time - self.start_time - 60 * mins
            duration = ""
            if mins == 0:
                duration = "%1.3f seconds" % secs
            elif mins == 1:
                duration = "1 minute and %1.3f seconds" % secs
            else:
                duration = "%d minutes and %1.3f seconds" % (mins,
                                                             secs)
            show_alert(
                "Minesweeper",
                f"Congratulations!\nYou won the game in {duration}.")
            self.restart_game()
            redraw()
            return

        # C
        # Check for game loss.
        revealed_mine_positions = \
            [pos for pos in self.all_valid_coords()
             if self[pos].has_mine()
             and self[pos].is_revealed()]

        # if any mine has been revealed, handle game loss
        # 'revealed_mine_positions' is a list, so this checks if the
        # list is non-empty
        if revealed_mine_positions:
            for pos in self.all_valid_coords():
                if not self[pos].has_flag():
                    self[pos].reveal()
            redraw()
            show_alert("Minesweeper", "Game over.\nTry again!")
            self.restart_game()
            redraw()
            return

        # D
        # game continues
        redraw()

    def try_generate_mines(self, field_x: int, field_y: int) -> None:

        if self.mines_have_been_generated:
            return

        possible_mine_locations = self.all_valid_coords()

        # don't place a mine where the user clicked
        possible_mine_locations.remove((field_x, field_y))

        # randomly place self.mine_count mines
        # random_sample prevents multiple mines from being generated
        # on the same tile
        mine_positions = random.sample(
            possible_mine_locations, self.mine_count)

        for pos in mine_positions:
            # turn all selected tiles into mines
            # see tile.py for more info on this
            self[pos].change_into_mine()

        self.mines_have_been_generated = True

        # save number of seconds since epoch (floating-point)
        self.start_time = time.time()

    def reveal_mines_from(self, field_x: int, field_y: int) -> None:
        queue = [(field_x, field_y)]
        complete: List[Tuple[int, int]] = []
        while queue: # while queue is non-empty
            if queue[0] in complete:
                del queue[0]
                continue
            # destructuring tuple assignment
            (current_x, current_y) = queue[0]
            # append tuple of current position
            #     ((double brackets required))
            complete.append((current_x, current_y))
            self[current_x, current_y].reveal()
            del queue[0]
            adjacent_tiles = self.adjacent_positions(
                current_x, current_y)
            # reveal tiles with adjacent mines, but don't search
            # any further (if they have adjacent mines) (or unless they
            # don't have adjacent mines)
            for adj_tile in adjacent_tiles:
                self[adj_tile].reveal()
                if self.adjacent_mine_count(*adj_tile) == 0:
                    queue.append(adj_tile)

    def primary_click(
            self,
            screen_coords: Tuple[float, float],
            apothem: float,
            redraw: Callable[[], None],
            show_alert: Callable[[str, str], None]) -> None:
        (screen_x, screen_y) = screen_coords
        (field_x, field_y) = self.screen_coordinates_to_game_position(
            screen_x, screen_y, apothem)

        # error handling
        if not self.is_position_valid(field_x, field_y):
            return
        if self[field_x, field_y].has_flag():
            # flags prevent accidental clicks, so don't
            # reveal anything if you click on a flag
            return

        # does nothing (nop) if mines have already been generated
        self.try_generate_mines(field_x, field_y)

        # reveal the tile the user clicked on
        # (it has already been check for validity)
        self[field_x, field_y].reveal()

        if self.adjacent_mine_count(field_x, field_y) > 0:
            # don't show any more tiles, just redraw,
            # check for game over and exit
            redraw()
            self.restart_if_game_is_over(redraw, show_alert)
            return

        self.reveal_mines_from(field_x, field_y)

        # finally check for game over, passing
        # the two function objects as this code
        # has no access to UI objects
        self.restart_if_game_is_over(redraw, show_alert)

    def secondary_click(
            self,
            screen_coords: Tuple[float, float],
            apothem: float,
            redraw: Callable[[], None],
            show_alert: Callable[[str, str], None]) -> None:
        (screen_x, screen_y) = screen_coords
        (field_x, field_y) = self.screen_coordinates_to_game_position(
            screen_x,
            screen_y,
            apothem)

        # error handling
        if not self.is_position_valid(field_x, field_y):
            return

        if not self[field_x, field_y].can_toggle_flag():
            return

        # toggle flag on right click
        if not self[field_x, field_y].has_flag(): # place a flag
            if self.flag_limit_reached():
                show_alert(
                    # mine count is always equal to flag limit
                    "Minesweeper",
                    "You've reached the flag "
                    + f"limit of {self.mine_count}.\n"
                    + "This means that at least one of your "
                    + "flags is incorrectly placed.\n"
                    + "Removing any incorrect flags and "
                    + "revealing those tiles will "
                    + "allow you to win the game.")
                return
            self[field_x, field_y].set_flag()
        else:
            self[field_x, field_y].unset_flag()

        self.restart_if_game_is_over(redraw, show_alert)

    def game_position_to_screen_coordinates(
            self,
            field_x: int,
            field_y: int,
            apothem: float) -> Tuple[float, float]:
       
        row_count = self.cell_count_in_row(field_y)
        max_row_count = self.highest_row_cell_count()

        # add one apothem to x for every y step
        # away from the center (in either direction)
        # for first cell at x = 0 in addition to subsequent cells
        screen_x = apothem * (max_row_count - row_count)
        # move over to correct cell
        screen_x += 2 * apothem * field_x
        # add another apothem to move from left
        # tile edge to tile center
        screen_x += apothem

        distance_tile_center_to_vertex = 2 * apothem / math.sqrt(3)
        vertical_tile_distance = 1.5 * distance_tile_center_to_vertex
        screen_y = field_y * vertical_tile_distance + \
            distance_tile_center_to_vertex
        # approximate, could be 1 off
        # in either direction
        screen_y = int(screen_y)

        return (screen_x, screen_y)

    def screen_coordinates_to_game_position(
            self,
            screen_x: float,
            screen_y: float,
            apothem: float) -> Tuple[int, int]:
        distance_tile_center_to_vertex = 2 * apothem / math.sqrt(3)
        # as above
        vertical_tile_distance = 1.5 * distance_tile_center_to_vertex
        field_y = round(
            (screen_y - distance_tile_center_to_vertex) \
                / vertical_tile_distance)

        row_count = self.cell_count_in_row(field_y)
        max_row_count = self.highest_row_cell_count()

        # move from tile center to left tile edge
        field_x = screen_x - apothem
        field_x -= apothem * (max_row_count - row_count)
        field_x = round(field_x / apothem / 2)
        return (field_x, field_y)
