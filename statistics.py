"""
This module is for running comparison statistics between different AI evaluation functions.
"""

import os
import time

import matplotlib.pyplot as plt

from board import CheckersBoard
from minimax import get_best_move, get_best_move_iddfs


def play_game(eval_func_r, eval_func_b, depth_r, depth_b, max_moves=150):
    """
    Plays a single game of checkers between two AI players with different evaluation functions.
    Returns the winner ('r', 'b', or 'draw'), and the total time and move count for each player.
    """
    board = CheckersBoard()
    move_count = 0
    total_time_r = 0
    total_time_b = 0
    moves_r = 0
    moves_b = 0

    while move_count < max_moves:
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            # The player whose turn it is has no moves, so they lose.
            winner = "b" if board.to_move == "r" else "r"
            break

        if board.to_move == "r":
            start_time = time.time()
            _, best_move, _, _ = get_best_move(board, depth_r, eval_func=eval_func_r)
            duration = time.time() - start_time
            total_time_r += duration
            moves_r += 1
        else:  # board.to_move == 'b'
            start_time = time.time()
            _, best_move, _, _ = get_best_move(board, depth_b, eval_func=eval_func_b)
            duration = time.time() - start_time
            total_time_b += duration
            moves_b += 1

        if best_move is None:
            # This can happen if the only moves lead to a loss and the AI decides no move is good.
            winner = "b" if board.to_move == "r" else "r"
            break

        board.execute_move(best_move)
        move_count += 1
    else:  # Loop finished without a break, meaning max_moves was reached
        winner = "draw"

    return winner, total_time_r, moves_r, total_time_b, moves_b


def main():
    """
    Main function to run the statistics.
    """

    eval_funcs = {
        "simple": CheckersBoard.eval,
        "smart": CheckersBoard.smart_eval,
        "advanced": CheckersBoard.eval_advanced,
    }

    depth = 3
    num_games = 10

    print(
        f"Running simulations with search depth {depth} for {num_games} games per matchup."
    )

    # Dictionary to store results
    results = {
        name: {"wins": 0, "total_time": 0, "total_moves": 0, "games_played": 0}
        for name in eval_funcs
    }

    func_names = list(eval_funcs.keys())

    for i in range(len(func_names)):
        for j in range(len(func_names)):
            if i == j:
                continue  # Don't play an eval against itself for now

            name1 = func_names[i]
            name2 = func_names[j]
            eval1 = eval_funcs[name1]
            eval2 = eval_funcs[name2]

            print(f"\n--- {name1} (Red) vs {name2} (Black) ---")

            for game_num in range(num_games):
                # Player 1 (eval1) as Red, Player 2 (eval2) as Black
                winner, total_r, moves_r, total_b, moves_b = play_game(
                    eval1, eval2, depth, depth
                )

                avg_time_r = total_r / moves_r if moves_r > 0 else 0
                avg_time_b = total_b / moves_b if moves_b > 0 else 0

                print(
                    f"  Game {game_num + 1}: Winner: {winner.upper()}, R_avg_time: {avg_time_r:.4f}s, B_avg_time: {avg_time_b:.4f}s"
                )

                if winner == "r":
                    results[name1]["wins"] += 1
                elif winner == "b":
                    results[name2]["wins"] += 1

                results[name1]["total_time"] += total_r
                results[name1]["total_moves"] += moves_r
                results[name1]["games_played"] += 1

                results[name2]["total_time"] += total_b
                results[name2]["total_moves"] += moves_b
                results[name2]["games_played"] += 1

    win_rates = []
    avg_times = []
    names = list(results.keys())

    print("\n\n--- Overall Statistics ---")
    for name in names:
        data = results[name]
        win_rate = (
            (data["wins"] / data["games_played"] * 100)
            if data["games_played"] > 0
            else 0
        )
        avg_time_per_move = (
            data["total_time"] / data["total_moves"] if data["total_moves"] > 0 else 0
        )

        win_rates.append(win_rate)
        avg_times.append(avg_time_per_move)

        print(f"Eval Function: {name}")
        print(
            f"  Win Rate: {win_rate:.2f}% ({data['wins']} wins out of {data['games_played']} games)"
        )
        print(f"  Average Time per Move: {avg_time_per_move:.4f}s")

    # Create visualizations
    temp_dir = os.environ.get("GEMINI_TMP_DIR", "/tmp")

    # Win Rate Plot
    plt.figure(figsize=(10, 6))
    plt.bar(names, win_rates, color=["blue", "green", "red"])
    plt.ylabel("Win Rate (%)")
    plt.title("Evaluation Function Win Rates")
    win_rate_path = os.path.join(temp_dir, "win_rates.png")
    plt.savefig(win_rate_path)
    print(f"\nWin rate plot saved to {win_rate_path}")

    # Time Performance Plot
    plt.figure(figsize=(10, 6))
    plt.bar(names, avg_times, color=["blue", "green", "red"])
    plt.ylabel("Average Time per Move (s)")
    plt.title("Average Time Per Move")
    avg_time_path = os.path.join(temp_dir, "avg_times.png")
    plt.savefig(avg_time_path)
    print(f"Average time plot saved to {avg_time_path}")


if __name__ == "__main__":
    main()
