# ui.py
'''
Interaction layer between player and the chess board.
Renders the board, reads moves as text, and reports what board.py says.
'''
from board import new_state, make_move, game_status, EMPTY, \
    WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK, position_key

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


def main():
    state = new_state()

    while True:
        print_board(state["board"])
        status = game_status(state)
        side = "White" if state["side"] == 1 else "Black"
        winner = "Black" if state["side"] == 1 else "White"

        if status == "checkmate":
            print(f"Checkmate! {winner} wins.")
            break
        if status == "stalemate":
            print("Draw by stalemate.")
            break
        if state["position_counts"].get(position_key(state), 0) >= 3:
        	claim = input("Threefold repetition, claim draw? y/n")
        	if claim == 'y':
        	    print("Draw by threefold repetition.")
                break
            #continue
        if state["position_counts"].get(position_key(state), 0) >= 5:
            print("Draw by fivefold repetition.")
            break
        if status == "draw":
            print("Draw (fifty-move rule or insufficient material).")
            break

        #if not legal_moves(state):
        #    return "checkmate" if checked else "stalemate"

        #if state["halfmove"] >= 100 or insufficient_material(state["board"]):
        #    return "draw"

        if status == "check":
            print("Check!")

        print(f"{side} to move")
        command = input("Chess> ").strip()

        if command == "quit":
            break

        result, new_state_ = make_move(state, command)

        if result == "need_promotion":
            result, new_state_ = make_move(state, command + " " + ask_promotion())

        if result == "invalid_input":
            print("Invalid input. Use the form: e2 e4")
        elif result == "illegal":
            print("Illegal move.")
        else:
            state = new_state_


if __name__ == "__main__":
    main()