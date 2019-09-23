from minesweeper import Minesweeper
import unittest

class MinesweeperTest(unittest.TestCase):
    def setUp(self):
        self.grid_size = 10
        self.number_of_mines = 10
        self.board_id = "1"
        self.minesweeper = Minesweeper(self.grid_size, self.number_of_mines, self.board_id)

    def tearDown(self):
        del self.grid_size
        del self.number_of_mines
        del self.board_id
        del self.minesweeper

    def test_setCustomSize(self):
        '''
        Check if grid is initialized properly
        :return:
        '''
        # Check grid size
        self.assertEqual(self.minesweeper.grid_size, self.grid_size, "Grid size did not match")

        # Check cell count
        self.assertEqual(self.grid_size * self.grid_size, self.minesweeper.cell_count, "Cell count did not match")

        # Check covered cells count
        self.assertEqual(len(self.minesweeper.covered_cells_set), self.grid_size * self.grid_size,
                         "Count of covered cells did not match")

        # Check uncovered cells count
        self.assertEqual(len(self.minesweeper.uncovered_cells_set), 0, "Count of covered cells did not match")

        # Check if start is not in mined_cells_set and numbered_cells_set
        self.assertEqual(1,
                         len(set([self.minesweeper.start]) - self.minesweeper.mines_set - self.minesweeper.numbered_cells_set),
                         "Starting cell is either a mine or a number")

    def test_setSize(self):
        # Selected cell should return true and should be removed from uncovered_cells_set
        cell_to_select = list(self.minesweeper.covered_cells_set - self.minesweeper.mines_set)[0]
        self.assertTrue(self.minesweeper.select_cell(cell_to_select), "Select cell other than mine should return True")
        self.assertTrue(cell_to_select not in self.minesweeper.covered_cells_set, "Selected cell still in covered_cells_set")
        self.assertTrue(cell_to_select in self.minesweeper.uncovered_cells_set, "Selected cell not in uncovered_cells_set")


    def test_prepareGame(self):
        # Selecting mine should return False
        mine_to_select = list(self.minesweeper.mines_set)[0]
        self.assertFalse(self.minesweeper.select_cell(mine_to_select), "Selecting mine should return False")

    def test_clickOn(self):
        # We should be able to play if there are covered cells
        self.assertTrue(self.minesweeper.check_if_we_can_play(), "We should be able to play before uncovering all cells")

        self.minesweeper.covered_cells_set = set()
        # We should not be able to play if there are uncovered cells
        self.assertFalse(self.minesweeper.check_if_we_can_play(), "We should not be able to play after uncovering all cells")


suite = unittest.TestLoader().loadTestsFromTestCase(MinesweeperTest)
unittest.TextTestRunner().run(suite)

