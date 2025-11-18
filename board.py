class Move:
    """
    Represents a move in the game, which can be a simple move or a multi-jump.
    """

    def __init__(self, path, captured_coords=None):
        self.path = path
        self.start = path[0]
        self.end = path[-1]
        self.captured = captured_coords if captured_coords else []

    def __repr__(self):
        if self.captured:
            return f"Move(path={self.path}, captured={self.captured})"
        else:
            return f"Move(path={self.path})"

    def __eq__(self, other):
        return isinstance(other, Move) and self.path == other.path


class CheckersBoard:
    def __init__(self, board=None, to_move="r"):
        if board is None:
            self.board = self._create_board()
            self.to_move = "r"
        else:
            self.board = board
            self.to_move = to_move

    def _create_board(self):
        board = [[" " for _ in range(8)] for _ in range(8)]
        for i in range(8):
            if i % 2 == 0:
                board[0][i] = "b"
                board[2][i] = "b"
                board[6][i] = "r"
            else:
                board[1][i] = "b"
                board[5][i] = "r"
                board[7][i] = "r"
        return board

    def get_possible_moves(self):
        """
        Gets all legal moves (as Move objects) for the current player.
        It enforces the mandatory jump rule.
        """
        # First check capturing moves, they are forced.
        all_jumps = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c].lower() == self.to_move:
                    all_jumps.extend(self._get_jumps_for_piece(r, c))

        # If there is at least one possible jump, return now
        if all_jumps:
            return all_jumps

        all_regulars = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c].lower() == self.to_move:
                    all_regulars.extend(self._get_regular_moves_for_piece(r, c))

        return all_regulars

    def get_moves_for_piece(self, r, c):
        """
        Gets all possible moves (as Move objects) for a single piece.
        """
        if self.board[r][c].lower() != self.to_move:
            return []

        # Jump moves are forced
        jumps = self._get_jumps_for_piece(r, c)
        if jumps:
            return jumps

        regulars = self._get_regular_moves_for_piece(r, c)
        return regulars

    def _get_jumps_for_piece(self, r, c):
        moves = []
        # Start the recursion with a path containing only the start position
        self._find_jump_sequences_recursive(
            [(r, c)], [], moves, self.board[r][c].isupper()
        )
        return moves

    def _find_jump_sequences_recursive(
        self, current_path, captured_this_sequence, final_moves, is_king
    ):
        r, c = current_path[-1]
        start_r, start_c = current_path[0]
        original_piece = self.board[start_r][start_c]

        effective_piece = original_piece.upper() if is_king else original_piece
        directions = self._get_directions_for_piece(effective_piece)

        found_jump_from_pos = False
        for dr, dc in directions:
            jump_over_r, jump_over_c = r + dr, c + dc
            land_r, land_c = r + 2 * dr, c + 2 * dc

            # Check if we are trying to jump over a piece we already captured
            if (jump_over_r, jump_over_c) in captured_this_sequence:
                continue

            if self.is_within_bounds(land_r, land_c):
                jump_over_piece = self.board[jump_over_r][jump_over_c]
                land_piece = self.board[land_r][land_c]

                # if target empty and piece jumped over is opponent
                if land_piece == " " and jump_over_piece.lower() not in (
                    " ",
                    self.to_move,
                ):
                    found_jump_from_pos = True
                    new_path = current_path + [(land_r, land_c)]
                    new_captured = captured_this_sequence + [(jump_over_r, jump_over_c)]

                    # Determine the king status for the NEXT hop.
                    new_is_king = is_king or (
                        (original_piece.lower() == "r" and land_r == 0)
                        or (original_piece.lower() == "b" and land_r == 7)
                    )

                    self._find_jump_sequences_recursive(
                        new_path, new_captured, final_moves, new_is_king
                    )

        # Base case: no more jumps can be made from this position, register it as a move
        if not found_jump_from_pos and len(current_path) > 1:
            final_moves.append(Move(current_path, captured_this_sequence))

    def _get_regular_moves_for_piece(self, r, c):
        moves = []
        piece = self.board[r][c]
        directions = self._get_directions_for_piece(piece)

        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            if self.is_within_bounds(new_r, new_c) and self.board[new_r][new_c] == " ":
                moves.append(Move([(r, c), (new_r, new_c)]))
        return moves

    def execute_move(self, move):
        """
        ** Assumes that move is valid **
        Executes a Move object on the board and mutates the board in place.
        """
        start_r, start_c = move.start
        piece = self.board[start_r][start_c]

        # Remove captured pieces from the board
        for cap_r, cap_c in move.captured:
            self.board[cap_r][cap_c] = " "

        # Move the piece along its path
        self.board[start_r][start_c] = " "
        end_r, end_c = move.end
        self.board[end_r][end_c] = piece

        # Handle promotion
        if (piece.lower() == "r" and end_r == 0) or (
            piece.lower() == "b" and end_r == 7
        ):
            self.board[end_r][end_c] = piece.upper()

        self.to_move = "b" if self.to_move == "r" else "r"

    def _get_directions_for_piece(self, piece):
        # Returns the valid move directions for a given piece type.
        if piece == "r":
            return [(-1, -1), (-1, 1)]
        if piece == "b":
            return [(1, -1), (1, 1)]
        # Kings can also move backwards
        if piece == "R" or piece == "B":
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return []

    def is_within_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def __str__(self):
        return "\n".join([" ".join(row) for row in self.board])

    def eval(self):
        score = 0
        for row in self.board:
            for cell in row:
                if cell == "r":
                    score += 1
                elif cell == "b":
                    score -= 1
                elif cell == "R":
                    score += 3
                elif cell == "B":
                    score -= 3
        return score


# for testing
if __name__ == "__main__":
    board = CheckersBoard()
    print(board)
    print(board.eval())
    print(board.get_possible_moves())
    while True:
        print("\n\n=====================================\n\n")
        moves = board.get_possible_moves()
        board.execute_move(moves[-1])
        print(board)
        print(board.eval())
        print(board.get_possible_moves())
