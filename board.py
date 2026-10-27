"""
board.py: chess rules and board state live here.

Squares are 0..63 (a1 = 0, h1 = 7, a8 = 56, h8 = 63).
Pieces: positive = white, negative = black (1 pawn .. 6 king).
A move is a tuple: (from_sq, to_sq, promotion) where promotion is None or 2..5.
"""

EMPTY = 0
WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
BP, BN, BB, BR, BQ, BK = -1, -2, -3, -4, -5, -6

KNIGHT_OFFSETS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
KING_OFFSETS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
DIAGONALS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ORTHOGONALS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
SLIDER_DIRS = {
    3: DIAGONALS,
    4: ORTHOGONALS,
    5: DIAGONALS + ORTHOGONALS,
}

PROMO_LETTERS = {"n": 2, "b": 3, "r": 4, "q": 5}

# Which castling right is lost when a piece moves from / to these squares
CASTLING_SQUARES = {0: "Q", 7: "K", 4: "KQ", 56: "q", 63: "k", 60: "kq"}


# board state

def initial_board():
    return [
        WR, WN, WB, WQ, WK, WB, WN, WR,
        WP, WP, WP, WP, WP, WP, WP, WP,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        BP, BP, BP, BP, BP, BP, BP, BP,
        BR, BN, BB, BQ, BK, BB, BN, BR,
    ]

'''
def new_state():
    return {
        "board": initial_board(),
        "side": 1,                       # 1 = white to move, -1 = black
        "castling": {"K": True, "Q": True, "k": True, "q": True},
        "enpassant": None,               # square a pawn can capture onto, or None
        "halfmove": 0,                   # for the fifty-move rule
        "fullmove": 1,
    }
'''
def new_state():
    state = {
        "board": initial_board(),
        "side": 1,
        "castling": {"K": True, "Q": True, "k": True, "q": True},
        "enpassant": None,
        "halfmove": 0,
        "fullmove": 1,
        "position_counts": {},
    }
    state["position_counts"][position_key(state)] = 1
    return state

def copy_state(state):
    new = dict(state)
    new["board"] = state["board"][:]
    new["castling"] = dict(state["castling"])
    return new

def position_key(state):
    ep = state["enpassant"]
    if ep is not None:
        board = state["board"]
        # only keep the ep square if a pawn can really capture onto it
        if not any(m[1] == ep and abs(board[m[0]]) == 1 for m in legal_moves(state)):
            ep = None
    return (
        tuple(state["board"]),
        state["side"],
        tuple(sorted(state["castling"].items())),
        ep,
    )

# attack geometry
def piece_attacks(board, sq):
    """Squares this piece attacks (whether or not they're occupied,
    and including squares holding its own pieces)."""
    piece = board[sq]
    kind = abs(piece)
    color = 1 if piece > 0 else -1
    f, r = sq % 8, sq // 8 # f -> file; r -> rank
    out = []

    if kind == 1:  # pawns attack diagonally forward only
        nr = r + color # nf -> new file
        for df in (-1, 1): # df -> direction (file); dr -> direction (rank)
            nf = f + df # nf -> new file
            if 0 <= nf < 8 and 0 <= nr < 8:
                out.append(nr * 8 + nf)
    elif kind in (2, 6):
        offsets = KNIGHT_OFFSETS if kind == 2 else KING_OFFSETS
        for df, dr in offsets:
            nf, nr = f + df, r + dr
            if 0 <= nf < 8 and 0 <= nr < 8:
                out.append(nr * 8 + nf)
    else:  # sliders
        for df, dr in SLIDER_DIRS[kind]:
            nf, nr = f + df, r + dr
            while 0 <= nf < 8 and 0 <= nr < 8:
                t = nr * 8 + nf
                out.append(t)
                if board[t] != EMPTY:  # blocked (we still attack the blocker)
                    break
                nf += df
                nr += dr
    return out


def is_square_attacked(board, sq, by_color):
    for i in range(64):
        p = board[i]
        if p != EMPTY and (p > 0) == (by_color > 0):
            if sq in piece_attacks(board, i):
                return True
    return False


def find_king(board, color):
    target = WK * color
    for i in range(64):
        if board[i] == target:
            return i
    return None


def in_check(board, color):
    king = find_king(board, color)
    return king is not None and is_square_attacked(board, king, -color)


# move generation
def pseudo_legal_moves(state):
    """Moves that obey piece movement rules but may leave own king in check."""
    board = state["board"]
    color = state["side"]
    moves = []

    for sq in range(64):
        piece = board[sq]
        if piece == EMPTY or (piece > 0) != (color > 0):
            continue
        kind = abs(piece)

        if kind == 1:
            _pawn_moves(state, sq, color, moves)
            continue

        for t in piece_attacks(board, sq):
            if board[t] * color <= 0:  # empty or enemy
                moves.append((sq, t, None))

        if kind == 6:
            _castling_moves(state, sq, color, moves)

    return moves


def _add_pawn_move(moves, sq, t):
    if t // 8 in (0, 7):
        for promo in (5, 4, 3, 2):
            moves.append((sq, t, promo))
    else:
        moves.append((sq, t, None))


def _pawn_moves(state, sq, color, moves):
    board = state["board"]
    f, r = sq % 8, sq // 8
    fwd = sq + 8 * color

    if board[fwd] == EMPTY:
        _add_pawn_move(moves, sq, fwd)
        start_rank = 1 if color == 1 else 6
        two = fwd + 8 * color
        if r == start_rank and board[two] == EMPTY:
            moves.append((sq, two, None))

    for t in piece_attacks(board, sq):  # diagonal captures
        if board[t] * color < 0 or t == state["enpassant"]:
            _add_pawn_move(moves, sq, t)


def _castling_moves(state, sq, color, moves):
    board = state["board"]
    base = 0 if color == 1 else 56
    if sq != base + 4:
        return
    king_right, queen_right = ("K", "Q") if color == 1 else ("k", "q")
    rook = WR * color
    enemy = -color

    if is_square_attacked(board, sq, enemy):  # can't castle out of check
        return

    # king side
    if (state["castling"][king_right] and board[base + 7] == rook
            and board[base + 5] == EMPTY and board[base + 6] == EMPTY
            and not is_square_attacked(board, base + 5, enemy)
            and not is_square_attacked(board, base + 6, enemy)):
        moves.append((sq, base + 6, None))

    # queen side
    if (state["castling"][queen_right] and board[base] == rook
            and board[base + 1] == EMPTY and board[base + 2] == EMPTY
            and board[base + 3] == EMPTY
            and not is_square_attacked(board, base + 3, enemy)
            and not is_square_attacked(board, base + 2, enemy)):
        moves.append((sq, base + 2, None))


def apply_move(state, move):
    """Return a NEW state with the move played. Assumes the move is pseudo-legal."""
    from_sq, to_sq, promo = move
    new = copy_state(state)
    b = new["board"]
    piece = b[from_sq]
    kind = abs(piece)
    color = 1 if piece > 0 else -1
    captured = b[to_sq]

    # en passant capture: pawn moves diagonally onto an empty square
    if kind == 1 and captured == EMPTY and from_sq % 8 != to_sq % 8:
        b[to_sq - 8 * color] = EMPTY
        captured = -color  # counts as a capture for the halfmove clock

    # castling: also move the rook
    if kind == 6 and abs(to_sq - from_sq) == 2:
        if to_sq > from_sq:
            b[from_sq + 1] = b[from_sq + 3]
            b[from_sq + 3] = EMPTY
        else:
            b[from_sq - 1] = b[from_sq - 4]
            b[from_sq - 4] = EMPTY

    b[to_sq] = piece
    b[from_sq] = EMPTY
    if promo is not None:
        b[to_sq] = promo * color

    # en passant target square
    if kind == 1 and abs(to_sq - from_sq) == 16:
        new["enpassant"] = (from_sq + to_sq) // 2
    else:
        new["enpassant"] = None

    # castling rights: lost when king/rook moves or a rook is captured
    for sq in (from_sq, to_sq):
        for right in CASTLING_SQUARES.get(sq, ""):
            new["castling"][right] = False

    new["halfmove"] = 0 if (kind == 1 or captured != EMPTY) else state["halfmove"] + 1
    if color == -1:
        new["fullmove"] += 1
    new["side"] = -color
    return new


def legal_moves(state):
    """Pseudo-legal moves that don't leave the mover's own king in check."""
    color = state["side"]
    result = []
    for move in pseudo_legal_moves(state):
        after = apply_move(state, move)
        if not in_check(after["board"], color):
            result.append(move)
    return result


# game status
def insufficient_material(board):
    pieces = [abs(p) for p in board if p != EMPTY and abs(p) != 6]
    if not pieces:
        return True
    return len(pieces) == 1 and pieces[0] in (2, 3)  # lone minor piece

def game_status(state):
    """'checkmate', 'stalemate', 'draw', 'check' or 'ongoing'."""
    checked = in_check(state["board"], state["side"])
    if not legal_moves(state):
        return "checkmate" if checked else "stalemate"
    if state["halfmove"] >= 100 or insufficient_material(state["board"]):
        return "draw"
    return "check" if checked else "ongoing"

def parse_square(name):
    if len(name) != 2 or name[0] not in "abcdefgh" or name[1] not in "12345678":
        return None
    return (int(name[1]) - 1) * 8 + (ord(name[0]) - ord("a"))

def square_name(sq):
    return "abcdefgh"[sq % 8] + str(sq // 8 + 1)

def move_to_text(move):
    """(from, to, promo) -> 'e2 e4' / 'e7 e8 q'. Handy for logging engine moves."""
    from_sq, to_sq, promo = move
    text = f"{square_name(from_sq)} {square_name(to_sq)}"
    if promo is not None:
        text += " " + "?nbrq"[promo - 1]
    return text

def parse_move(state, text):
    """
    Turn user text like 'e2 e4' (or 'e7 e8 q') into a legal move tuple.
    Returns (status, move):
      'invalid_input'  - couldn't parse
      'illegal'        - parsed but not legal
      'need_promotion' - legal pawn move to last rank, no piece given
      'ok'             - move is the legal move tuple
    """
    parts = text.split()
    if len(parts) not in (2, 3):
        return "invalid_input", None

    from_sq, to_sq = parse_square(parts[0]), parse_square(parts[1])
    if from_sq is None or to_sq is None:
        return "invalid_input", None

    promo = None
    if len(parts) == 3:
        promo = PROMO_LETTERS.get(parts[2].lower())
        if promo is None:
            return "invalid_input", None

    candidates = [m for m in legal_moves(state) if m[0] == from_sq and m[1] == to_sq]
    if not candidates:
        return "illegal", None

    if promo is None and candidates[0][2] is not None:
        return "need_promotion", None

    chosen = [m for m in candidates if m[2] == promo]
    if not chosen:
        return "illegal", None
    return "ok", chosen[0]

def play_move(state, move):
    """Commit a legal move tuple for real. Returns the NEW state (records repetition).
    Engines use apply_move() while searching and play_move() only for the final choice."""
    new = apply_move(state, move)
    counts = dict(state["position_counts"])   # copy once per real move
    key = position_key(new)
    counts[key] = counts.get(key, 0) + 1
    new["position_counts"] = counts
    return new

def make_move(state, text):
    """Text convenience wrapper: returns (status, state)."""
    status, move = parse_move(state, text)
    if status != "ok":
        return status, state
    return "ok", play_move(state, move)