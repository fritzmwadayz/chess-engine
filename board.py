EMPTY = 0

WP = 1
WN = 2
WB = 3
WR = 4
WQ = 5
WK = 6

BP = -1
BN = -2
BB = -3
BR = -4
BQ = -5
BK = -6


def create_position():
    return {
        "board": [EMPTY] * 64,
        "side": 1,
        "castling": {"K": True, "Q": True, "k": True, "q": True},
        "enpassant": None,
        "halfmove": 0,
        "fullmove": 1,
        "history": [],
        "position_counts": {}
    }

def hash_position(pos):
    return (
        tuple(pos["board"]),
        pos["side"],
        tuple(sorted(pos["castling"].items())),
        pos["enpassant"]
    )

def update_repetition(pos):
    key = hash_position(pos)
    pos["position_counts"][key] = pos["position_counts"].get(key, 0) + 1
    return pos["position_counts"][key]

def is_threefold(pos):
    key = hash_position(pos)
    return pos["position_counts"].get(key, 0) >= 3