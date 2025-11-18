import unittest

from board import CheckersBoard, Move


class TestCheckersBoard(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def assertMovesEqual(self, found_moves, expected_moves):
        """Helper to compare lists of Move objects, ignoring order."""
        self.assertCountEqual(found_moves, expected_moves)
        # For older python versions, assertCountEqual might not use __eq__.
        # This provides a more robust check.
        found_set = set(map(repr, found_moves))
        expected_set = set(map(repr, expected_moves))
        self.assertEqual(found_set, expected_set)

    def test_initial_moves(self):
        """Test the valid opening moves for the starting player (red)."""
        board = CheckersBoard()
        moves = board.get_possible_moves()
        expected_moves = [
            Move([(5, 1), (4, 0)]),
            Move([(5, 1), (4, 2)]),
            Move([(5, 3), (4, 2)]),
            Move([(5, 3), (4, 4)]),
            Move([(5, 5), (4, 4)]),
            Move([(5, 5), (4, 6)]),
            Move([(5, 7), (4, 6)]),
        ]
        self.assertMovesEqual(moves, expected_moves)

    def test_forced_capture(self):
        """Test that a jump is forced, ignoring any available regular moves."""
        board_layout = [
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", "b", " ", " ", " ", " "],
            ["r", " ", "r", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
        ]
        board = CheckersBoard(board=board_layout, to_move="r")
        moves = board.get_possible_moves()
        expected_moves = [Move(path=[(5, 2), (3, 4)], captured_coords=[(4, 3)])]
        self.assertMovesEqual(moves, expected_moves)

    def test_chain_jump_single_branch(self):
        """Test a standard non-branching double jump."""
        board_layout = [
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", "b", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", "b", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "b", " ", " ", " ", " ", " "],
            [" ", "r", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
        ]
        board = CheckersBoard(board=board_layout, to_move="r")
        moves = board.get_possible_moves()
        expected_moves = [
            Move(
                path=[(6, 1), (4, 3), (2, 5), (0, 7)],
                captured_coords=[(5, 2), (3, 4), (1, 6)],
            )
        ]
        self.assertMovesEqual(moves, expected_moves)

    def test_chain_jump_multiple_branches(self):
        """Test a jump sequence where the player has a choice of capture paths."""
        board_layout = [
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "b", " ", "b", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "b", " ", " ", " ", " ", " "],
            [" ", "r", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
        ]
        board = CheckersBoard(board=board_layout, to_move="r")
        moves = board.get_possible_moves()
        expected_moves = [
            Move(
                path=[(6, 1), (4, 3), (2, 1)],
                captured_coords=[(5, 2), (3, 2)],
            ),
            Move(
                path=[(6, 1), (4, 3), (2, 5)],
                captured_coords=[(5, 2), (3, 4)],
            ),
        ]
        self.assertMovesEqual(moves, expected_moves)

    def test_kinging_mid_chain_jump(self):
        """Test a piece becoming a king mid-jump and using its new powers."""
        board_layout = [
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "b", " ", "b", " ", " ", " "],
            [" ", "r", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
        ]
        board = CheckersBoard(board=board_layout, to_move="r")
        moves = board.get_possible_moves()
        expected_moves = [
            Move(
                path=[(2, 1), (0, 3), (2, 5)],
                captured_coords=[(1, 2), (1, 4)],
            )
        ]
        self.assertMovesEqual(moves, expected_moves)

    def test_king_captures(self):
        """Test a king's ability to capture both forwards and backwards."""
        board_layout = [
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", "b", "b", " ", " ", " ", " "],
            [" ", " ", " ", "R", " ", " ", " ", " "],
            [" ", " ", "b", "r", "b", " ", "b", " "],
            [" ", "b", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", "r"],
        ]
        board = CheckersBoard(board=board_layout, to_move="r")
        moves = board.get_possible_moves()
        expected_moves = [
            Move(path=[(3, 3), (1, 1)], captured_coords=[(2, 2)]),
            Move(path=[(3, 3), (5, 5), (3, 7)], captured_coords=[(4, 4), (4, 6)]),
        ]
        self.assertMovesEqual(moves, expected_moves)


if __name__ == "__main__":
    unittest.main()
