import tkinter as tk
from time import perf_counter

import board
from board import CheckersBoard
from minimax import get_best_move, get_best_move_iddfs, minimax


class CheckersGUI:
    """
    GUI around the existing Checkers engine + minimax AI.

    - Uses `CheckersBoard` for all rules / move generation.
    - Uses `get_best_move` from `minimax.py` when AI is enabled.
    - Human always plays red; AI (if enabled) plays black.
    """

    def __init__(self, ai_enabled: bool = True, ai_depth: int = 10):
        self.board = CheckersBoard()
        self.selected_square = None
        self.valid_moves = []
        self.square_size = 60

        self.ai_enabled = ai_enabled
        self.ai_depth = ai_depth
        self.ai_plays_black = True  # human = red, AI = black

        # --- Stats ---
        self.stats = {
            "ai_depth": self.ai_depth,
            "game_branching_factor": 0,
            "avg_game_branching_factor": 0.0,
            "current_eval": 0.0,
            "ai_eval": 0.0,
            "move_time": 0.0,
            "explored_states": 0,
            "cache_hits": 0,
            "ai_search_branching_factor": 0.0,
        }
        self.branching_factor_history = []
        self.human_best_move = None

        self.root = tk.Tk()
        self.root.title("Checkers")
        self.root.resizable(False, False)
        self.show_best_move = tk.BooleanVar()
        self.force_capture = tk.BooleanVar(value=board.FORCED_CAPTURE)
        self.eval_function_name = tk.StringVar(value="Simple Eval")
        self.depth_scheduler_name = tk.StringVar(value="Static")
        self.depth_scheduler = "Static"
        self.time_limit = 3.0
        self.eval_func = CheckersBoard.eval

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for the board
        canvas_size = 8 * self.square_size
        self.canvas = tk.Canvas(main_frame, width=canvas_size, height=canvas_size)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)

        # Stats panel
        stats_frame = tk.Frame(main_frame, padx=10, pady=10)
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self._init_stats_panel(stats_frame)

        self.status_label = tk.Label(self.root, text="Red's turn", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.update_game_state()
        self.draw_board()

        # If AI starts, let it move.
        if self.ai_enabled and self.is_ai_turn():
            self.root.after(500, self.make_ai_move)

    def _init_stats_panel(self, parent: tk.Frame):
        """Creates the labels for the stats panel."""
        tk.Label(parent, text="--- Statistics ---", font=("Arial", 12, "bold")).pack(
            anchor="w"
        )

        self.stats_labels = {
            "ai_depth": tk.Label(parent, text=f"AI Depth: {self.ai_depth}"),
            "game_branching_factor": tk.Label(
                parent, text="Game Branching Factor: N/A"
            ),
            "avg_game_branching_factor": tk.Label(
                parent, text="Avg Game Branching Factor: N/A"
            ),
            "ai_search_branching_factor": tk.Label(
                parent, text="AI Search Branching Factor: N/A"
            ),
            "current_eval": tk.Label(parent, text="Current Eval: N/A"),
            "ai_eval": tk.Label(parent, text="AI Eval: N/A"),
            "move_time": tk.Label(parent, text="Last Move Time: N/A"),
            "explored_states": tk.Label(parent, text="Explored States: N/A"),
            "cache_hits": tk.Label(parent, text="Cache Hits: N/A"),
        }

        for label in self.stats_labels.values():
            label.pack(anchor="w")

        # Best move checkbox
        tk.Checkbutton(
            parent,
            text="Show Best Move",
            variable=self.show_best_move,
            onvalue=True,
            offvalue=False,
            command=self._update_and_draw,
        ).pack(anchor="w", pady=5)

        tk.Checkbutton(
            parent,
            text="Forced Capture",
            variable=self.force_capture,
            onvalue=True,
            offvalue=False,
            command=self._toggle_forced_capture,
        ).pack(anchor="w", pady=5)

        # Reset button
        tk.Button(parent, text="Reset Game", command=self.reset_game).pack(
            anchor="w", pady=10
        )

        # Eval function dropdown
        tk.Label(parent, text="Evaluation Function:", font=("Arial", 10, "bold")).pack(
            anchor="w", pady=(10, 0)
        )
        tk.OptionMenu(
            parent,
            self.eval_function_name,
            "Simple Eval",
            "Smart Eval",
            "Advanced Eval",
            command=self._update_eval_func,
        ).pack(anchor="w")

        tk.Label(parent, text="Depth scheduler:", font=("Arial", 10, "bold")).pack(
            anchor="w", pady=(10, 0)
        )
        tk.OptionMenu(
            parent,
            self.depth_scheduler_name,
            "Static",
            "Iterative Deepening",
            command=self._update_depth_scheduler,
        ).pack(anchor="w")

        # AI Depth slider
        tk.Label(parent, text="AI Depth:", font=("Arial", 10, "bold")).pack(
            anchor="w", pady=(10, 0)
        )
        self.depth_scale = tk.Scale(
            parent,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=tk.IntVar(value=self.ai_depth),
            command=self._update_ai_depth,
        )
        self.depth_scale.pack(anchor="w")

        # AI Time Limit slider
        tk.Label(
            parent, text="AI Time Limit (IDDFS):", font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(10, 0))
        self.time_limit_scale = tk.Scale(
            parent,
            from_=0.1,
            to=10.0,
            orient=tk.HORIZONTAL,
            variable=tk.DoubleVar(value=self.time_limit),
            bigincrement=0.1,
            command=self._update_time_limit,
        )
        self.time_limit_scale.pack(anchor="w")

    def _update_ai_depth(self, value):
        """Updates the AI depth from the slider."""
        self.ai_depth = int(value)
        self.stats["ai_depth"] = self.ai_depth
        minimax.cache_clear()
        self._update_and_draw()

    def _update_depth_scheduler(self, value):
        """Updates the depth scheduler from the dropdown."""
        self.depth_scheduler = value
        minimax.cache_clear()
        self._update_and_draw()

    def _update_time_limit(self, value):
        """Updates the AI time limit from the slider."""
        self.time_limit = float(value)
        self.stats["ai_time_limit"] = self.time_limit
        minimax.cache_clear()
        self._update_and_draw()

    def _update_and_draw(self):
        self.update_game_state()
        self.draw_board()

    def _update_eval_func(self, _=None):
        """Updates the self.eval_func based on the dropdown selection."""
        if self.eval_function_name.get() == "Smart Eval":
            self.eval_func = CheckersBoard.smart_eval
        elif self.eval_function_name.get() == "Advanced Eval":
            self.eval_func = CheckersBoard.eval_advanced
        else:
            self.eval_func = CheckersBoard.eval
        minimax.cache_clear()
        # After changing the eval function, we need to re-evaluate the position
        self._update_and_draw()

    def _toggle_forced_capture(self):
        """Toggles the FORCED_CAPTURE global in the board module."""
        board.FORCED_CAPTURE = self.force_capture.get()
        minimax.cache_clear()
        self._update_and_draw()

    def reset_game(self):
        """Resets the game to its initial state."""
        self.board = CheckersBoard()
        self.selected_square = None
        self.valid_moves = []

        # Reset stats
        self.stats = {
            "ai_depth": self.ai_depth,
            "game_branching_factor": 0,
            "avg_game_branching_factor": 0.0,
            "current_eval": 0.0,
            "ai_eval": 0.0,
            "move_time": 0.0,
            "explored_states": 0,
            "cache_hits": 0,
            "ai_search_branching_factor": 0.0,
        }
        self.branching_factor_history = []
        self.human_best_move = None

        self.update_game_state()
        self.draw_board()

        # If AI starts, let it move.
        if self.ai_enabled and self.is_ai_turn():
            self.root.after(500, self.make_ai_move)

    # Turns / AI helpers  ---------------

    def is_ai_turn(self) -> bool:
        if not self.ai_enabled:
            return False
        if self.ai_plays_black:
            return self.board.to_move == "b"
        return self.board.to_move == "r"

    def make_ai_move(self):
        if not self.is_ai_turn():
            return

        self.status_label.config(text="AI is thinking...")
        self.root.update_idletasks()

        start_time = perf_counter()
        ai_eval, best_move, explored_states, avg_branching_factor = (
            None,
            None,
            None,
            None,
        )
        if self.depth_scheduler == "Static":
            ai_eval, best_move, explored_states, avg_branching_factor = get_best_move(
                self.board, self.ai_depth, eval_func=self.eval_func
            )
        elif self.depth_scheduler == "Iterative Deepening":
            ai_eval, best_move, explored_states, avg_branching_factor = (
                get_best_move_iddfs(
                    self.board, self.ai_depth, self.time_limit, eval_func=self.eval_func
                )
            )
        end_time = perf_counter()

        if best_move is not None:
            self.board.execute_move(best_move)
            self.stats["ai_eval"] = ai_eval
            self.stats["move_time"] = end_time - start_time
            self.stats["explored_states"] = explored_states
            self.stats["cache_hits"] = minimax.cache_info().hits
            self.stats["ai_search_branching_factor"] = avg_branching_factor

        self.selected_square = None
        self.valid_moves = []
        self.update_game_state()
        self.draw_board()

    # Drawing ---------------

    def draw_board(self):
        self.canvas.delete("all")

        # Draw squares + pieces
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                # Checkerboard pattern
                if (row + col) % 2 == 0:
                    color = "#DDB88C"  # light square
                else:
                    color = "#8B4513"  # dark square

                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, outline="black", width=1
                )

                piece = self.board.get_piece(row, col)
                if piece != " ":
                    self._draw_piece(row, col, piece)

        # Highlight currently selected square
        if self.selected_square is not None:
            row, col = self.selected_square
            x1 = col * self.square_size
            y1 = row * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=3)

        # Mark valid destination squares for the selected piece
        for move in self.valid_moves:
            if move.start != self.selected_square:
                continue
            end_row, end_col = move.end
            x1 = end_col * self.square_size
            y1 = end_row * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_oval(
                x1 + 6, y1 + 6, x2 - 6, y2 - 6, outline="green", width=3
            )

        # Show best move for human
        if self.show_best_move.get() and self.human_best_move:
            self._draw_best_move_arrow(self.human_best_move)

    def _draw_best_move_arrow(self, move):
        start_row, start_col = move.start
        end_row, end_col = move.end

        x1 = start_col * self.square_size + self.square_size // 2
        y1 = start_row * self.square_size + self.square_size // 2
        x2 = end_col * self.square_size + self.square_size // 2
        y2 = end_row * self.square_size + self.square_size // 2

        self.canvas.create_line(
            x1, y1, x2, y2, arrow=tk.LAST, fill="blue", width=3, dash=(4, 4)
        )

    def _draw_piece(self, row: int, col: int, piece: str):
        x1 = col * self.square_size
        y1 = row * self.square_size
        center_x = x1 + self.square_size // 2
        center_y = y1 + self.square_size // 2
        radius = self.square_size // 3

        if piece.lower() == "r":
            fill_color = "#DC143C"  # red
            outline_color = "black"
        else:
            fill_color = "#000000"  # black
            outline_color = "white"

        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=fill_color,
            outline=outline_color,
            width=2,
        )

        # Draw a simple "K" for kings
        if piece.isupper():
            self.canvas.create_text(
                center_x,
                center_y,
                text="K",
                fill="gold",
                font=("Arial", 14, "bold"),
            )

    #  Mouse interaction ----------

    def on_click(self, event):
        # Ignore clicks while AI is moving
        if self.is_ai_turn():
            return

        col = event.x // self.square_size
        row = event.y // self.square_size

        if not self.board.is_within_bounds(row, col):
            return

        if self.selected_square is not None:
            self._handle_move_or_reselect(row, col)
        else:
            self._handle_select(row, col)

    def _handle_select(self, row: int, col: int):
        piece = self.board.get_piece(row, col)
        if piece.lower() == self.board.to_move:
            self.selected_square = (row, col)
            self.valid_moves = self.board.get_moves_for_piece(row, col)
            self.draw_board()

    def _handle_move_or_reselect(self, row: int, col: int):
        start_row, start_col = self.selected_square
        moves = self.board.get_moves_for_piece(start_row, start_col)

        # Try to find a move that ends at the clicked square
        for move in moves:
            if move.end == (row, col):
                self.board.execute_move(move)
                self.selected_square = None
                self.valid_moves = []
                self.update_game_state()
                self.draw_board()

                # After human move, let AI respond if enabled
                if self.ai_enabled and self.is_ai_turn():
                    self.root.after(500, self.make_ai_move)
                return

        # If clicked on another of your own pieces, switch selection
        piece = self.board.get_piece(row, col)
        if piece.lower() == self.board.to_move:
            self.selected_square = (row, col)
            self.valid_moves = self.board.get_moves_for_piece(row, col)
        else:
            self.selected_square = None
            self.valid_moves = []

        self.draw_board()

    # Status / game over ----------

    def update_game_state(self):
        """
        Updates all game-state related information and stats.
        """
        # Update turn status label
        if self.board.to_move == "r":
            self.status_label.config(text="Red's turn")
        else:
            self.status_label.config(text="Black's turn")

        # Check for game over
        moves = self.board.get_possible_moves()
        if not moves:
            winner = "Black" if self.board.to_move == "r" else "Red"
            self.status_label.config(text=f"{winner} wins!")
            self.human_best_move = None
            self.stats["current_eval"] = 0  # Or some other terminal value
        else:
            # Pre-calculate human's best move if it's their turn
            if not self.is_ai_turn():
                (
                    eval_val,
                    self.human_best_move,
                    explored_states,
                    avg_branching_factor,
                ) = None, None, None, None
                if self.depth_scheduler == "Static":
                    (
                        eval_val,
                        self.human_best_move,
                        explored_states,
                        avg_branching_factor,
                    ) = get_best_move(
                        self.board, self.ai_depth, eval_func=self.eval_func
                    )
                elif self.depth_scheduler == "Iterative Deepening":
                    (
                        eval_val,
                        self.human_best_move,
                        explored_states,
                        avg_branching_factor,
                    ) = get_best_move_iddfs(
                        self.board,
                        self.ai_depth,
                        self.time_limit,
                        eval_func=self.eval_func,
                    )
                self.stats["current_eval"] = eval_val
                self.stats["explored_states"] = explored_states
                self.stats["cache_hits"] = minimax.cache_info().hits
                self.stats["ai_search_branching_factor"] = avg_branching_factor
            else:
                self.human_best_move = None
                # When it's AI's turn, the "current eval" is from the AI's perspective
                self.stats["current_eval"] = self.eval_func(self.board)

        # Update stats data
        self._update_stats_data(moves)
        # Refresh the GUI labels
        self._update_stats_labels()

    def _update_stats_data(self, moves):
        """Calculates and updates the self.stats dictionary."""
        # Branching factor
        current_branching_factor = len(moves)
        if current_branching_factor > 0:
            self.branching_factor_history.append(current_branching_factor)

        avg_branching = (
            sum(self.branching_factor_history) / len(self.branching_factor_history)
            if self.branching_factor_history
            else 0
        )
        self.stats["game_branching_factor"] = current_branching_factor
        self.stats["avg_game_branching_factor"] = avg_branching

        # Current board evaluation
        self.stats["current_eval"] = self.eval_func(self.board)

    def _update_stats_labels(self):
        """Updates the statistics panel labels from self.stats."""
        self.stats_labels["ai_depth"].config(text=f"AI Depth: {self.stats['ai_depth']}")
        self.stats_labels["game_branching_factor"].config(
            text=f"Game Branching Factor: {self.stats['game_branching_factor']}"
        )
        self.stats_labels["avg_game_branching_factor"].config(
            text=f"Avg Game Branching Factor: {self.stats['avg_game_branching_factor']:.2f}"
        )
        self.stats_labels["ai_search_branching_factor"].config(
            text=f"AI Search Branching Factor: {self.stats['ai_search_branching_factor']:.2f}"
        )
        self.stats_labels["current_eval"].config(
            text=f"Current Eval: {self.stats['current_eval']:.2f}"
        )
        self.stats_labels["ai_eval"].config(
            text=f"AI Eval: {self.stats['ai_eval']:.2f}"
        )
        self.stats_labels["move_time"].config(
            text=f"Last Move Time: {self.stats['move_time']:.3f}s"
        )
        self.stats_labels["explored_states"].config(
            text=f"Explored States: {self.stats['explored_states']}"
        )
        self.stats_labels["cache_hits"].config(
            text=f"Cache Hits: {self.stats['cache_hits']}"
        )

    #  Main loop ----------

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Default it is: human (red) vs AI (black)
    game = CheckersGUI(ai_enabled=True, ai_depth=4)
    game.run()
