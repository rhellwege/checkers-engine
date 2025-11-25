from copy import deepcopy
from board import CheckersBoard, Move


def minimax(board: CheckersBoard, depth: int, alpha: float, beta: float, maximizing: bool):
    """
    Minimaxes the current board and returns (best_score, best_move).
    """
    # Terminal condition
    if depth == 0:
        return board.eval(), None

    possible_moves = board.get_possible_moves()

    if not possible_moves:
        return (board.eval(), None)

    # maximizing player (r) 
    if maximizing:
        best_value = float("-inf")
        best_move = None

        for move in possible_moves:
            # simulate move
            new_board = deepcopy(board)
            new_board.execute_move(move)

            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False)

            if evaluation > best_value:
                best_value = evaluation
                best_move = move
            # alpha-beta pruning for efficiency
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break  

        return best_value, best_move

    # minimizing player (b) 
    else:
        best_value = float("inf")
        best_move = None

        for move in possible_moves:
            new_board = deepcopy(board)
            new_board.execute_move(move)

            evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True)

            if evaluation < best_value:
                best_value = evaluation
                best_move = move

            beta = min(beta, best_value)
            if beta <= alpha:
                break

        return best_value, best_move


def get_best_move(board: CheckersBoard, depth: int = 5):
    """
    Returns the best move for the player that is going to play.
    """
    is_red_to_move = board.to_move == "r"
    _, best_move = minimax(
        board,
        depth,
        alpha=float("-inf"),
        beta=float("inf"),
        maximizing=is_red_to_move,
    )
    return best_move