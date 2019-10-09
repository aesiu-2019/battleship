from enum import Enum
from random import randint
from copy import copy, deepcopy

class OpposingState(Enum):
	UNKNOWN = 1
	GUESSED = 2

class SelfState(Enum):
	SHIP = 1
	MISS = 2

class Appearance(Enum):
	UNKNOWN = 1
	MISS = 2
	SUNK = 3


# Managers the actual boards and state of the boards
class PlayBoard:
# UPDATE THESE VALUES TO CHANGE BASIC GAME DIMENSIONS
	battleshipSizes = [5, 4, 3, 3, 2]
	rowCount = 10
	colCount = 10

	def __init__(self, sourceFile):
		# the actual board of ships
		self.board = []
		# where the opponant has guessed on this board
		self.guessedBoard = []
		# tracking history, for potential future analysis
		self.guessesMade = []
		self.shipsPlaced = []

		# metadata to help run the game faster
		self.activeShips = 0
		self.lastGuessRow = -1
		self.lastGuessCol = -1
		self.lastHitRow = -1
		self.lastHitCol = -1

		for i in range(self.rowCount):
			row = []
			for j in range(self.colCount):
				row.append(OpposingState.UNKNOWN)
			self.guessedBoard.append(row)
		if (sourceFile == None):
			# no explicit map, generate a random one
			self.generateRandomBaord()
			return
		f = open(sourceFile)
		# first row should just be markers
		f.readline()
		for i in range(self.rowCount):
			inputRow = f.readline()
			row = []
			self.board.append(row)
			for j in range(self.colCount):
				# offset of 4 to reach the first coordinate, then 2 chars for each
				elementIndex = (j*2) + 4
				if (len(inputRow) > elementIndex and inputRow[elementIndex] == "X"):
					row.append(SelfState.SHIP)
					self.placeShipSegment(i, j)
				else:
					row.append(SelfState.MISS)
			


	def generateRandomBaord(self):
		for i in range(self.rowCount):
			row = []
			for j in range(self.colCount):
				row.append(SelfState.MISS)
			self.board.append(row)

		for ship in self.battleshipSizes:
			while True:
				direction = randint(0,1)
				# 0 will be horizontal, 1 will be vertical
				colStart = randint(0, self.colCount - 1)
				rowStart = randint(0, self.rowCount - 1)
				if (direction == 0):
					# horizontal, so the row must start at least a little before the edge
					colStart = randint(0, self.colCount - ship - 1)
				else:
					rowStart = randint(0, self.rowCount - ship - 1)
				if(self.validShipPlacement(rowStart, colStart, ship, direction)):
					## ship can be placed, so let's place it
					self.placeShip(rowStart, colStart, ship, direction)
					break;

	def placeShip(self, rowStart, colStart, ship, direction):
		column = colStart
		row = rowStart
		for coord in range(ship):
			self.placeShipSegment(row, column)
			if (direction == 0):
				column = column + 1
			else:
				row = row + 1

	def placeShipSegment(self, row, column):
		self.activeShips = self.activeShips + 1
		self.board[row][column] = SelfState.SHIP
		self.shipsPlaced.append([row, column])


	def validShipPlacement(self, rowStart, colStart, ship, direction):
		column = colStart
		row = rowStart

		for coord in range(ship):
			if (self.board[row][column] == SelfState.SHIP):
				return False
			if (direction == 0):
				column = column + 1
			else:
				row = row + 1
		return True

	def printSelfBoard(self):
		self.printBoard(True)
	def printOpposingBoard(self):
		self.printBoard(False)

	def printBoard(self, asSelf):
		line = "  |"
		
		for i in range(self.rowCount):
			line = line + " " +chr(65 + i)
		print(line)
		for i in range(self.rowCount):
			line = str(i + 1).zfill(2) + "|"
			for j in range(self.colCount):
				char = self.getRepresentingChar(i, j, asSelf)
				
				line = line + " " + char
			print(line)

	def getRepresentingChar(self, row, column, asSelf):
		guessedState = self.guessedBoard[row][column]
		if (guessedState == OpposingState.UNKNOWN and not asSelf):
			# unknown to someone else just looks blank
			return " "
		state = self.board[row][column]
		if (state == SelfState.MISS):
			if(guessedState == OpposingState.GUESSED):
				# they guessed it, but it was a miss
				return "O"
			else:
				# nothing is there but that's not known yet
				return " "
		else:
			if(guessedState == OpposingState.GUESSED):
				# it's sunk
				return "X"
			else:
				# it's there but still hidden
				return "-"


	def guess(self, row, column):
		# the actual code for when a guess is made
		if (self.guessedBoard[row][column] == OpposingState.GUESSED):
			raise IOError("already guessed")

		self.guessedBoard[row][column] = OpposingState.GUESSED
		self.lastGuessRow = row
		self.lastGuessCol = column
		isHit = self.board[row][column] == SelfState.SHIP
		self.guessesMade.append([row, column, isHit])
		if (not isHit):
			return
		self.activeShips = self.activeShips - 1
		self.lastHitRow = row
		self.lastHitCol = column

	def nuke(self):
		# only used for debugging and ending games
		for i in range(self.rowCount):
			for j in range(self.colCount):
				try: 
					self.guess(i,j)
				except IOError as err:
					pass

	def getAppearance(self, row, column):
		if (self.guessedBoard[row][column] == OpposingState.UNKNOWN):
			return Appearance.UNKNOWN
		if (self.board[row][column] == SelfState.SHIP):
			return Appearance.SUNK
		return Appearance.MISS

