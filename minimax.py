from functools import lru_cache

from board import CheckersBoard, Move

# Global counters for AI search stats.
# This is not thread-safe, but for this application it is acceptable.
EXPLORED_STATES = 0
TOTAL_BRANCHES = 0


@lru_cache(maxsize=None)
def minimax(
    board: CheckersBoard,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    eval_func,
):
    """
    Minimaxes the current board and returns (best_score, best_move).
    """
    global EXPLORED_STATES, TOTAL_BRANCHES
    EXPLORED_STATES += 1

    # Terminal condition
    if depth == 0:
        return eval_func(board), None

    possible_moves = board.get_possible_moves()
    TOTAL_BRANCHES += len(possible_moves)

    if not possible_moves:
        return eval_func(board), None

    # maximizing player (r)
    if maximizing:
        best_value = float("-inf")
        best_move = None

        for move in possible_moves:
            # simulate move
            undo_info = board.execute_move(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, False, eval_func)
            board.undo_move(undo_info)

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
            undo_info = board.execute_move(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, True, eval_func)
            board.undo_move(undo_info)

            if evaluation < best_value:
                best_value = evaluation
                best_move = move

            beta = min(beta, best_value)
            if beta <= alpha:
                break

        return best_value, best_move


def get_best_move(board: CheckersBoard, depth: int = 5, eval_func=CheckersBoard.eval):
    """
    Returns the best move for the player that is going to play.
    """
    global EXPLORED_STATES, TOTAL_BRANCHES
    EXPLORED_STATES = 0
    TOTAL_BRANCHES = 0

    is_red_to_move = board.to_move == "r"
    eval, best_move = minimax(
        board,
        depth,
        alpha=float("-inf"),
        beta=float("inf"),
        maximizing=is_red_to_move,
        eval_func=eval_func,
    )

    avg_branching_factor = (
        TOTAL_BRANCHES / EXPLORED_STATES if EXPLORED_STATES > 0 else 0
    )

    return eval, best_move, EXPLORED_STATES, avg_branching_factor
