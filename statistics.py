"""
This module is for running comparison statistics between different AI evaluation functions.
"""

import os
import time
from collections import defaultdict

import matplotlib.pyplot as plt

from board import CheckersBoard
from minimax import minimax


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
        if board.to_move == "r":
            start_time = time.time()
            _, best_move = minimax(
                board, depth_r, float("-inf"), float("inf"), True, eval_func_r
            )
            minimax.cache_clear()
            duration = time.time() - start_time
            total_time_r += duration
            moves_r += 1
        else:  # board.to_move == 'b'
            start_time = time.time()
            _, best_move = minimax(
                board, depth_b, float("-inf"), float("inf"), False, eval_func_b
            )
            minimax.cache_clear()
            duration = time.time() - start_time
            total_time_b += duration
            moves_b += 1

        if best_move is None:
            winner = "b" if board.to_move == "r" else "r"
            break

        board.execute_move(best_move)

        if not board.get_possible_moves():
            winner = "b" if board.to_move == "r" else "r"
            break

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

    depth = 8
    num_games = 100

    print(
        f"Running simulations with search depth {depth} for {num_games} games per matchup."
    )

    overall_results = {
        name: {"wins": 0, "total_time": 0, "total_moves": 0, "games_played": 0}
        for name in eval_funcs
    }
    matchup_results = defaultdict(
        lambda: defaultdict(lambda: {"p1_wins": 0, "p2_wins": 0, "draws": 0})
    )

    func_names = list(eval_funcs.keys())

    for i in range(len(func_names)):
        for j in range(len(func_names)):
            if i == j:
                continue

            name1 = func_names[i]
            name2 = func_names[j]
            eval1 = eval_funcs[name1]
            eval2 = eval_funcs[name2]

            print(f"\n--- {name1} (Red) vs {name2} (Black) ---")

            for game_num in range(num_games):
                winner, total_r, moves_r, total_b, moves_b = play_game(
                    eval1, eval2, depth, depth
                )
                print(
                    f"  Game {game_num + 1}: Winner: {winner.upper()} Moves: {moves_b + moves_r} Total Time: {total_b + total_r}"
                )

                if winner == "r":
                    matchup_results[name1][name2]["p1_wins"] += 1
                elif winner == "b":
                    matchup_results[name1][name2]["p2_wins"] += 1
                else:  # draw
                    matchup_results[name1][name2]["draws"] += 1

                # Update overall stats
                overall_results[name1]["games_played"] += 1
                overall_results[name2]["games_played"] += 1
                overall_results[name1]["total_time"] += total_r
                overall_results[name2]["total_time"] += total_b
                overall_results[name1]["total_moves"] += moves_r
                overall_results[name2]["total_moves"] += moves_b
                if winner == "r":
                    overall_results[name1]["wins"] += 1
                elif winner == "b":
                    overall_results[name2]["wins"] += 1

    temp_dir = "/tmp"

    win_rates = []
    avg_times = []
    names = list(overall_results.keys())

    print("\n\n--- Overall Statistics ---")
    for name in names:
        data = overall_results[name]
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

    # Overall Win Rate Plot
    plt.figure(figsize=(10, 6))
    plt.bar(names, win_rates, color=["blue", "green", "red"])
    plt.ylabel("Overall Win Rate (%)")
    plt.title(f"Overall Win Rates (Depth: {depth}, Games per Matchup: {num_games})")
    win_rate_path = os.path.join(temp_dir, "overall_win_rates.png")
    plt.savefig(win_rate_path)
    print(f"\nOverall win rate plot saved to {win_rate_path}")

    # Overall Time Performance Plot
    plt.figure(figsize=(10, 6))
    plt.bar(names, avg_times, color=["blue", "green", "red"])
    plt.ylabel("Average Time per Move (s)")
    plt.title(
        f"Overall Average Time Per Move (Depth: {depth}, Games per Matchup: {num_games})"
    )
    avg_time_path = os.path.join(temp_dir, "overall_avg_times.png")
    plt.savefig(avg_time_path)
    print(f"Overall average time plot saved to {avg_time_path}")

    # Matchup-specific plots
    for name1, matchups in matchup_results.items():
        for name2, results in matchups.items():
            labels = [f"{name1} (Red) Wins", f"{name2} (Black) Wins", "Draws"]
            values = [results["p1_wins"], results["p2_wins"], results["draws"]]

            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(labels, values, color=["red", "black", "grey"])

            ax.set_ylabel("Number of Games")
            ax.set_title(f"Matchup: {name1} (Red) vs. {name2} (Black)")
            ax.text(
                0.5,
                -0.1,
                f"Search Depth: {depth}, Games Played: {num_games}",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )

            for bar in bars:
                yval = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0, yval, int(yval), va="bottom"
                )

            plot_filename = f"matchup_{name1}_vs_{name2}.png"
            plot_path = os.path.join(temp_dir, plot_filename)
            plt.savefig(plot_path, bbox_inches="tight")
            plt.close(fig)

            print(f"\nMatchup plot saved to {plot_path}")


if __name__ == "__main__":
    main()
