import tkinter as tk

from board import CheckersBoard
from minimax import get_best_move


class CheckersGUI:
    """
    GUI around the existing Checkers engine + minimax AI.

    - Uses `CheckersBoard` for all rules / move generation.
    - Uses `get_best_move` from `minimax.py` when AI is enabled.
    - Human always plays red; AI (if enabled) plays black.
    """

    def __init__(self, ai_enabled: bool = True, ai_depth: int = 5):
        self.board = CheckersBoard()
        self.selected_square = None
        self.valid_moves = []
        self.square_size = 60

        self.ai_enabled = ai_enabled
        self.ai_depth = ai_depth
        self.ai_plays_black = True  # human = red, AI = black

        self.root = tk.Tk()
        self.root.title("Checkers")
        self.root.resizable(False, False)

        canvas_size = 8 * self.square_size
        self.canvas = tk.Canvas(self.root, width=canvas_size, height=canvas_size)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.status_label = tk.Label(self.root, text="Red's turn", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.draw_board()

        # If AI starts  let it move.
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

        _, best_move = get_best_move(self.board, self.ai_depth)
        if best_move is not None:
            self.board.execute_move(best_move)

        self.selected_square = None
        self.valid_moves = []
        self.update_status()
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

                piece = self.board.board[row][col]
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
        piece = self.board.board[row][col]
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
                self.update_status()
                self.draw_board()

                # After human move, let AI respond if enabled
                if self.ai_enabled and self.is_ai_turn():
                    self.root.after(500, self.make_ai_move)
                return

        # If clicked on another of your own pieces, switch selection
        piece = self.board.board[row][col]
        if piece.lower() == self.board.to_move:
            self.selected_square = (row, col)
            self.valid_moves = self.board.get_moves_for_piece(row, col)
        else:
            self.selected_square = None
            self.valid_moves = []

        self.draw_board()

    # Status / game over ----------

    def update_status(self):
        if self.board.to_move == "r":
            self.status_label.config(text="Red's turn")
        else:
            self.status_label.config(text="Black's turn")

        eval, best_move = get_best_move(self.board, self.ai_depth)
        self.status_label.config(text=f"Best move: {best_move}, Evaluation: {eval}")
        moves = self.board.get_possible_moves()
        if not moves:
            winner = "Black" if self.board.to_move == "r" else "Red"
            self.status_label.config(text=f"{winner} wins!")

    #  Main loop ----------

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Default it is: human (red) vs AI (black)
    game = CheckersGUI(ai_enabled=True, ai_depth=10)
    game.run()

    # if you want to do a human vs human game you can  do:
    # game = CheckersGUI(ai_enabled=False)
    # game.run()
