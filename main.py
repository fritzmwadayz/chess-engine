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

'''
PIECE_SYMBOLS = {
    EMPTY: " ",
    WP: "P", WN: "N", WB: "B", WR: "R", WQ: "Q", WK: "K",
    BP: "p", BN: "n", BB: "b", BR: "r", BQ: "q", BK: "k",
}
'''

PIECE_SYMBOLS = {
    EMPTY: " ",

    BP: "♙", BN: "♘", BB: "♗", # symbols flipped for dark terminal visibility
    BR: "♖", BQ: "♕", BK: "♔",

    WP: "♟", WN: "♞", WB: "♝",
    WR: "♜", WQ: "♛", WK: "♚",
}

def print_board(board):
    print("    a   b   c   d   e   f   g   h")
    print("  ┌───┬───┬───┬───┬───┬───┬───┬───┐")

    for rank in range(8):
        rank_num = 8 - rank

        row = []
        for file in range(8):
            square = rank * 8 + file
            row.append(PIECE_SYMBOLS[board[square]])

        print(f"{rank_num} │ " + " │ ".join(row) + " │")

        if rank < 7:
            print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")

    print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
    print("    a   b   c   d   e   f   g   h")

board = [
    BR, BN, BB, BQ, BK, BB, BN, BR,
    BP, BP, BP, BP, BP, BP, BP, BP,

    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,

    WP, WP, WP, WP, WP, WP, WP, WP,
    WR, WN, WB, WQ, WK, WB, WN, WR
]

def parse_square(name):
	file = ord(name[0]) - ord('a')
	rank = 8 - int(name[1])

	return rank * 8 + file

def make_move(board, move):
	start, end = move.split()
	from_sq = parse_square(start)
	to_sq = parse_square(end)
	if board[from_sq] == EMPTY:
		print("No piece there.")
	side = 1
	if side == 1:
	    print("White to move")
	else:
	    print("Black to move")

	piece = board[from_sq]
	if piece * side <= 0:
	    print("Not your piece.")

	else:
		board[to_sq] = board[from_sq]
		board[from_sq] = EMPTY

		side = -side

while True:
	print_board(board)

	command = input("Chess> ")

	if command == "quit":
		break

	make_move(board, command)