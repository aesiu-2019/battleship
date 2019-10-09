from playBoard import PlayBoard, Appearance
from random import randint


# given a board, this should provide guesses on where to fire next
class BoardInterface:
	def __init__(self, playBoard):
		self.guessMade = False
		self._playBoard = playBoard
		self.activeShips = playBoard.activeShips
		# guessers board is only the appearances, so it can't cheat
		self.board = []
		self.lastHitRow = playBoard.lastHitRow
		self.lastHitCol = playBoard.lastHitCol
		self.lastGuessRow = playBoard.lastGuessRow
		self.lastGuessCol = playBoard.lastGuessCol
		self.battleshipSizes = playBoard.battleshipSizes
		for i in range(PlayBoard.rowCount):
			row = []
			for j in range(PlayBoard.colCount):
				row.append(playBoard.getAppearance(i, j))
			self.board.append(row)

	def getLastHit(self):
		return [self.lastHitRow, self.lastHitCol]

	def getLastGuess(self):
		return [self.lastGuessRow, self.lastGuessCol]

	def getFullBoardAppearance(self):
		return self.board

	def getBoardAppearance(self, row, column):
		if (row > PlayBoard.rowCount - 1 or column > PlayBoard.colCount -1 or row < 0 or column < 0):
			raise IOError("Element " + str(row) + " , " + str(column) + " is out of bounds of the board")
		return self.board[row][column]

	def getRemainingShips(self):
		return self.activeShips

	def hasGuessBeenMade(self):
		return self.guessMade

	def getShipSizes(self):
		return self.battleshipSizes

	def postGuess(self, row, column):
		if (self.guessMade):
			raise IOError("Guess has already been made")
		self._playBoard.guess(row, column)
		self.guessMade = True

	
	