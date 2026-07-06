import os

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

	for rank in range(7,-1,-1):
		rank_num = rank + 1

		row = []
		for file in range(8):
			square = rank * 8 + file
			row.append(PIECE_SYMBOLS[board[square]])

		print(f"{rank_num} │ " + " │ ".join(row) + " │")

		if rank > 0:
			print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")

	print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
	print("    a   b   c   d   e   f   g   h")

"""board = [
	BR, BN, BB, BQ, BK, BB, BN, BR,
	BP, BP, BP, BP, BP, BP, BP, BP,

	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,

	WP, WP, WP, WP, WP, WP, WP, WP,
	WR, WN, WB, WQ, WK, WB, WN, WR
]"""

##Moves:
# Pawns: +16, +8, +9, +7
# Bishops: +9, -9, +7, -7
# Knights: -6, +6, -10. +10, -15, +15, -17, +17
# Rooks: +1, -1, +8, -8
# Queen: +1, -1, +8, -8, +9, -9, +7, -7
# King: +1, -1, +7, -7, +8, -8

#pawn move
def pawn_move(from_sq, to_sq):
	diff = to_sq - from_sq

	if diff*board[from_sq] < 0: #stop backward moves
		return False
	if abs(diff) == 16:
		if board[(from_sq+to_sq)//2] != 0: #stop double push if pawn blocked
			return False
		if board[to_sq] != 0: # stop forward capture
			return False
		return from_sq//8 == 6 or from_sq//8==1
	if abs(diff) == 8:
		return board[to_sq] == 0 #stop forward capture
	if abs(diff) == 7 or abs(diff) == 9:
		if abs(from_sq//8 - to_sq//8) == 1: #for captures make sure ranks are different by 1
			if board[from_sq] == -1: # black should not capture black
				return board[to_sq] > 0
			if board[from_sq] == 1: # white should not capture white
				return board[to_sq] < 0
	return False

def bishop_move(from_sq, to_sq):
	moves = {7,9}

	if from_sq//8 == to_sq//8:
		return False

	if from_sq%8 == to_sq%8:
		return False

def knight_move(from_sq, to_sq):
	moves = {6,10,15,17}
	diff = to_sq - from_sq
	if abs(diff) in moves:
		if from_sq//8 == to_sq//8:
			return False
		if from_sq%8 == to_sq%8:
			return False
		if ((from_sq%8) - (to_sq%8)) == 2 and abs((from_sq//2) - (to_sq//2)) == 1:
			return True
		if ((from_sq%8) - (to_sq%8)) == 1 and abs((from_sq//2) - (to_sq//2)) == 2:
		#	return True
	return False

def rook_move(from_sq, to_sq):
	moves = {1,8}
	if move in moves:
		pass

def queen_move(from_sq, to_sq):
	moves = {1,7,8,9}
	if move in moves:
		pass

def king_move(from_sq, to_sq):
	pass

board = [
	WR, WN, WB, WQ, WK, WB, WN, WR,
	WP, WP, WP, WP, WP, WP, WP, WP,
	0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
    BP, BP, BP, BP, BP, BP, BP, BP,
    BR, BN, BB, BQ, BK, BB, BN, BR,
]

def parse_square(name):
	file = ord(name[0]) - ord('a')
	rank = int(name[1]) - 1 #8 - int(name[1]) 
	return rank * 8 + file

# Track turns
current_turn = 1 

def make_move(board, move):
	global current_turn

	start, end = move.split()
	from_sq = parse_square(start)
	to_sq = parse_square(end)

	if board[from_sq] == EMPTY:
		print("No piece there.")
		return

	piece = board[from_sq]
	if piece * current_turn < 0:
		print("Not your piece.")
		return

	# pawn move
	if abs(piece) == 1:
		if pawn_move(from_sq, to_sq) is False:
			print("Invalid move.")
			return
		if to_sq//8 == 0 or to_sq//8 == 7:
			print("You've reached a promotion square")
			print("What piece do you want?")
			print("Enter 2 for bishop\n 3 for knight\n 4 for rook\n or 5 for queen")
			new_piece = int(input("Choice:"))
			
			while new_piece not in range(2, 6):
				print("Invalid choice try again.")
				print("Enter 2 for bishop\n 3 for knight\n 4 for rook\n or 5 for queen")
				new_piece = int(input("Choice:"))
			board[from_sq] = new_piece * piece

	# bishop move
	if abs(piece) == 2:
		if bishop_move(from_sq, to_sq) is False:
			print("Invalid move.")
			return

	# knight move
	if abs(piece) == 3:
		if knight_move(from_sq, to_sq) is False:
			print("Invalid move.")
			return

	# rook move
	if abs(piece) == 4:
		pass

	# queen move
	if abs(piece) == 5:
		pass

	# king move
	if abs(piece) == 6:
		pass

	board[to_sq] = board[from_sq]
	board[from_sq] = EMPTY

    # flip turn for next loop
	current_turn = -current_turn 


while True:
	#print("\033[2J\033[H")
	#os.system("clear")
	print_board(board)

	if current_turn == 1:
		print("White to move")
	else:
		print("Black to move")

	command = input("Chess> ")

	if command == "quit":
		break

	make_move(board, command)