import array

FORCED_CAPTURE = True

PIECE_TO_INT = {" ": 0, "r": 1, "b": 2, "R": 3, "B": 4}
INT_TO_PIECE = {v: k for k, v in PIECE_TO_INT.items()}

WEIGHT_PIECES = 1
WEIGHT_MOBILITY = 0.3
WEIGHT_STARTING_PIECES = 0.1
WEIGHT_KING = 2


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


class UndoInfo:
    """
    A small container to hold the information needed to undo a move.
    """

    def __init__(self, move, piece_moved, captured_pieces, was_promoted):
        self.move = move
        self.piece_moved = piece_moved
        self.captured_pieces = captured_pieces
        self.was_promoted = was_promoted


class CheckersBoard:
    def __init__(self, board=None, to_move="r"):
        if board is None:
            self.board = self._create_board()
            self.to_move = "r"
        else:
            self.board = board
            self.to_move = to_move

    def get_piece(self, r, c):
        return INT_TO_PIECE[self.board[r * 8 + c]]

    def set_piece(self, r, c, piece):
        self.board[r * 8 + c] = PIECE_TO_INT[piece]

    def _create_board(self):
        board = array.array("b", [0] * 64)
        for i in range(8):
            if i % 2 == 0:
                board[0 * 8 + i] = PIECE_TO_INT["b"]
                board[2 * 8 + i] = PIECE_TO_INT["b"]
                board[6 * 8 + i] = PIECE_TO_INT["r"]
            else:
                board[1 * 8 + i] = PIECE_TO_INT["b"]
                board[5 * 8 + i] = PIECE_TO_INT["r"]
                board[7 * 8 + i] = PIECE_TO_INT["r"]
        return board

    def get_possible_moves(self):
        """
        Gets all legal moves (as Move objects) for the current player.
        It enforces the mandatory jump rule if FORCED_CAPTURE is True.
        """
        all_jumps = []
        for r in range(8):
            for c in range(8):
                if self.get_piece(r, c).lower() == self.to_move:
                    all_jumps.extend(self._get_jumps_for_piece(r, c))

        if FORCED_CAPTURE and all_jumps:
            return all_jumps

        all_regulars = []
        for r in range(8):
            for c in range(8):
                if self.get_piece(r, c).lower() == self.to_move:
                    all_regulars.extend(self._get_regular_moves_for_piece(r, c))

        if not FORCED_CAPTURE:
            return all_jumps + all_regulars
        else:  # FORCED_CAPTURE is true, but there were no jumps
            return all_regulars

    def get_moves_for_piece(self, r, c):
        """
        Gets all possible moves (as Move objects) for a single piece.
        """
        if self.get_piece(r, c).lower() != self.to_move:
            return []

        moves = self.get_possible_moves()
        # filter
        moves = [move for move in moves if move.path[0] == (r, c)]

        return moves

    def _get_jumps_for_piece(self, r, c):
        moves = []
        # Start the recursion with a path containing only the start position
        self._find_jump_sequences_recursive(
            [(r, c)], [], moves, self.get_piece(r, c).isupper()
        )
        return moves

    def _find_jump_sequences_recursive(
        self, current_path, captured_this_sequence, final_moves, is_king
    ):
        r, c = current_path[-1]
        start_r, start_c = current_path[0]
        original_piece = self.get_piece(start_r, start_c)

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
                jump_over_piece = self.get_piece(jump_over_r, jump_over_c)
                land_piece = self.get_piece(land_r, land_c)

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
        piece = self.get_piece(r, c)
        directions = self._get_directions_for_piece(piece)

        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            if (
                self.is_within_bounds(new_r, new_c)
                and self.get_piece(new_r, new_c) == " "
            ):
                moves.append(Move([(r, c), (new_r, new_c)]))
        return moves

    def execute_move(self, move):
        """
        ** Assumes that move is valid **
        Executes a Move object on the board and mutates the board in place.
        Returns an UndoInfo object to revert the move.
        """
        start_r, start_c = move.start
        end_r, end_c = move.end
        piece = self.get_piece(start_r, start_c)

        # Store info for undo
        captured_pieces = []
        for cap_r, cap_c in move.captured:
            captured_pieces.append(((cap_r, cap_c), self.get_piece(cap_r, cap_c)))

        was_promoted = not piece.isupper() and (
            (piece.lower() == "r" and end_r == 0)
            or (piece.lower() == "b" and end_r == 7)
        )
        undo_info = UndoInfo(move, piece, captured_pieces, was_promoted)

        # Remove captured pieces from the board
        for cap_r, cap_c in move.captured:
            self.set_piece(cap_r, cap_c, " ")

        # Move the piece along its path
        self.set_piece(start_r, start_c, " ")
        end_r, end_c = move.end

        # Handle promotion
        if (piece.lower() == "r" and end_r == 0) or (
            piece.lower() == "b" and end_r == 7
        ):
            self.set_piece(end_r, end_c, piece.upper())
        else:
            self.set_piece(end_r, end_c, piece)

        self.to_move = "b" if self.to_move == "r" else "r"
        return undo_info

    def undo_move(self, undo_info):
        """
        Reverts the board to the state before the move was executed.
        """
        move = undo_info.move
        start_r, start_c = move.start
        end_r, end_c = move.end

        # Switch player back
        self.to_move = "b" if self.to_move == "r" else "r"

        # Move piece back from end to start
        # The piece to move back is the original piece, before any promotion
        self.set_piece(start_r, start_c, undo_info.piece_moved)
        self.set_piece(end_r, end_c, " ")  # The landing square is now empty

        # Restore captured pieces
        for (cap_r, cap_c), piece in undo_info.captured_pieces:
            self.set_piece(cap_r, cap_c, piece)

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
        lines = []
        for r in range(8):
            row_str = " ".join([self.get_piece(r, c) for c in range(8)])
            lines.append(row_str)
        return "\n".join(lines)

    def __eq__(self, other):
        return isinstance(other, CheckersBoard) and self.board == other.board

    def __hash__(self):
        return hash((self.board.tobytes(), self.to_move))

    def copy(self):
        return CheckersBoard(self.board[:], self.to_move)

    def eval(self):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece == "r":
                    score += 1
                elif piece == "b":
                    score -= 1
                elif piece == "R":
                    score += 3
                elif piece == "B":
                    score -= 3
        return score

    def smart_eval(self):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece == "r":
                    score += 1 + (7 - r) * 0.1
                elif piece == "b":
                    score -= 1 + r * 0.1
                elif piece == "R":
                    score += WEIGHT_KING
                elif piece == "B":
                    score -= WEIGHT_KING
        return score

    def eval_advanced(self):
        piece_score = self.smart_eval() * WEIGHT_PIECES
        mobility_score = len(self.get_possible_moves()) * WEIGHT_MOBILITY
        # count starting pieces:
        starting_pieces = 0
        if self.to_move == "r":
            for i in range(8):
                if self.get_piece(i, 0) == "r" or self.get_piece(i, 0) == "R":
                    starting_pieces += 1
        elif self.to_move == "b":
            for i in range(8):
                if self.get_piece(i, 7) == "b" or self.get_piece(i, 7) == "B":
                    starting_pieces += 1
        starter_score = starting_pieces * WEIGHT_STARTING_PIECES
        return piece_score + mobility_score + starter_score


# for testing
if __name__ == "__main__":
    board = CheckersBoard()
    print(board)
    print(board.eval())
    print(board.get_possible_moves())
    while True:
        print("\n\n=====================================\n\n")
        moves = board.get_possible_moves()
        if not moves:
            break
        board.execute_move(moves[-1])
        print(board)
        print(board.eval())
        print(board.get_possible_moves())
