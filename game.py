# game.py
'''
Neutral game loop. Asks whoever's turn it is for a move via player.get_move(state) and plays it.
'''
from board import new_state, legal_moves, play_move, game_status, move_to_text
from ui import print_board


def play(white, black, show=True, max_plies=None):
    """Run a game. Returns (result, final_state).
    result: 'checkmate', 'stalemate', 'draw', 'quit' or 'max_plies'."""
    players = {1: white, -1: black}
    state = new_state()
    plies = 0

    while True:
        if show:
            print_board(state["board"])

        status = game_status(state)
        if status == "checkmate":
            if show:
                print(f"Checkmate! {players[-state['side']].name} wins.")
            return "checkmate", state
        if status in ("stalemate", "draw"):
            if show:
                print(f"Game drawn ({status}).")
            return status, state
        if status == "check" and show:
            print("Check!")

        if max_plies is not None and plies >= max_plies:
            return "max_plies", state

        player = players[state["side"]]
        if show:
            print(f"{player.name} to move")

        move = player.get_move(state)
        if move is None:
            return "quit", state

        # safety net: catches illegal moves from a buggy engine
        if move not in legal_moves(state):
            raise ValueError(f"{player.name} returned an illegal move: {move}")

        if show:
            print(f"{player.name} plays {move_to_text(move)}")
        state = play_move(state, move)
        plies += 1


def main():
    from ui import HumanPlayer

    print("1) Human vs Human\n2) Human (white) vs Engine\n3) Engine vs Engine")
    choice = input("Mode: ").strip()

    if choice == "1":
        play(HumanPlayer("White"), HumanPlayer("Black"))
    else:
        from engine import EnginePlayer   # imported lazily so mode 1 works without it
        if choice == "2":
            play(HumanPlayer("You"), EnginePlayer())
        elif choice == "3":
            play(EnginePlayer("Engine A"), EnginePlayer("Engine B"))
        else:
            print("Unknown mode.")


if __name__ == "__main__":
    main()
