import random
from time import time

from board import CheckersBoard, Move

# Global counters for AI search stats.
# This is not thread-safe, but for this application it is acceptable.
EXPLORED_STATES = 0
TOTAL_BRANCHES = 0


# @lru_cache(maxsize=None)
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
        best_moves = []

        for move in possible_moves:
            # simulate move
            undo_info = board.execute_move(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, False, eval_func)
            board.undo_move(undo_info)

            if evaluation > best_value:
                best_value = evaluation
                best_moves = [move]
            elif evaluation == best_value:
                best_moves.append(move)

            # alpha-beta pruning for efficiency
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break

        return best_value, random.choice(best_moves) if best_moves else None

    # minimizing player (b)
    else:
        best_value = float("inf")
        best_moves = []

        for move in possible_moves:
            undo_info = board.execute_move(move)
            evaluation, _ = minimax(board, depth - 1, alpha, beta, True, eval_func)
            board.undo_move(undo_info)

            if evaluation < best_value:
                best_value = evaluation
                best_moves = [move]
            elif evaluation == best_value:
                best_moves.append(move)

            beta = min(beta, best_value)
            if beta <= alpha:
                break

        return best_value, random.choice(best_moves) if best_moves else None


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


def get_best_move_iddfs(
    board: CheckersBoard, max_depth, max_dur_s, eval_func=CheckersBoard.eval
):
    """
    Returns the best move for the player that is going to play using iterative deepening depth-first search.
    Either uses max depth or max duration, whichever is reached first.
    """
    start_time = time()

    best_move = None
    evaluation = None
    total_explored_states = 0
    avg_branching_factor = 0
    last_completed_depth = 0

    for depth in range(1, max_depth + 1):
        if time() - start_time >= max_dur_s:
            print(
                f"Time limit reached. Stopping search at depth {last_completed_depth}."
            )
            break

        (
            eval_iter,
            move_iter,
            explored_iter,
            avg_branching_iter,
        ) = get_best_move(board, depth, eval_func=eval_func)

        # The results from the deepest fully searched depth are the most reliable.
        evaluation = eval_iter
        best_move = move_iter
        avg_branching_factor = avg_branching_iter
        total_explored_states += explored_iter  # a running total
        last_completed_depth = depth
    else:  # This runs if the loop completes without `break`.
        print(f"Max depth of {max_depth} reached.")

    return evaluation, best_move, total_explored_states, avg_branching_factor
