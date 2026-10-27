# ui.py
'''
Everything a human needs: rendering the board and a HumanPlayer
that turns typed text into a move.
'''
from board import parse_move, EMPTY, \
    WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK

PIECE_SYMBOLS = {
    EMPTY: " ",

    BP: "♙", BN: "♘", BB: "♗",  # symbols flipped for dark terminal visibility
    BR: "♖", BQ: "♕", BK: "♔",

    WP: "♟", WN: "♞", WB: "♝",
    WR: "♜", WQ: "♛", WK: "♚",
}


def print_board(board):
    print("    a   b   c   d   e   f   g   h")
    print("  ┌───┬───┬───┬───┬───┬───┬───┬───┐")

    for rank in range(7, -1, -1):
        row = [PIECE_SYMBOLS[board[rank * 8 + file]] for file in range(8)]
        print(f"{rank + 1} │ " + " │ ".join(row) + " │")
        if rank > 0:
            print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")

    print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
    print("    a   b   c   d   e   f   g   h")


def ask_promotion():
    while True:
        choice = input("Promote to (n/b/r/q): ").strip().lower()
        if choice in ("n", "b", "r", "q"):
            return choice
        print("Invalid choice, try again.")


class HumanPlayer:
    """Player interface: get_move(state) -> move tuple, or None to quit."""

    def __init__(self, name="Human"):
        self.name = name

    def get_move(self, state):
        while True:
            command = input("Chess> ").strip()
            if command == "quit":
                return None

            status, move = parse_move(state, command)
            if status == "need_promotion":
                status, move = parse_move(state, command + " " + ask_promotion())

            if status == "ok":
                return move
            if status == "invalid_input":
                print("Couldn't read that. Use the form: e2 e4")
            else:
                print("Illegal move.")