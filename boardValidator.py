from playBoard import PlayBoard, SelfState
from copy import copy, deepcopy
from ruleSet import RuleSet


# used to validate that a given board has valid ship placement
class BoardValidator:
	def __init__(self, playBoard):
		self.board = playBoard.board
		self.battleshipSizes = RuleSet.battleshipSizes

	def validate(self):
		totalShips = 0
		for ship in self.battleshipSizes:
			totalShips = totalShips + ship
		for i in range(RuleSet.rowCount):
			for j in range(RuleSet.colCount):
				if (self.board[i][j] == SelfState.SHIP):
					totalShips = totalShips - 1
		if (totalShips != 0):
			# not even the right number of ships on the field
			return False
		shipArray = self.battleshipSizes.copy()
		workingBoard = deepcopy(self.board)
		return self.isValid(workingBoard, shipArray)

	def isValid(self, workingBoard, shipArray):
		if (self.isEmpty(workingBoard) and len(shipArray) == 0):
			return True
		for i in range(RuleSet.rowCount):
			for j in range(RuleSet.colCount):
				if (workingBoard[i][j] == SelfState.SHIP):
					for ship in list(set(shipArray)):
						if (self.attemptShipPlacement(workingBoard, shipArray, ship, i, j, 0)
							or self.attemptShipPlacement(workingBoard, shipArray, ship, i, j, 1)):
							return True
					# we found the first corner ship but nothing in the ship array could place it 
					# and still be valid.  Will not be possible to place anything else and still eliminate this ship
					return False
		return False
	def attemptShipPlacement(self, workingBoard, shipArray, ship, row, column, direction):
		# try to shove a ship here,
		if self.canShipFit(workingBoard, ship, row, column, direction):
			newBoard = deepcopy(workingBoard)
			self.sink(newBoard, row, column, ship, direction)
			newShips = shipArray.copy()
			newShips.remove(ship)
			# if a ship fits, see if the rest of the board is valid
			if (self.isValid(newBoard, newShips)):
				return True
		return False

	def canShipFit(self, workingBoard, ship, row, column, direction):
		for i in range(ship):
			if (column >= RuleSet.colCount or row >= RuleSet.rowCount):
				return False
			if (workingBoard[row][column] == SelfState.MISS):
				return False
			if (direction == 0):
				column = column + 1
			else:
				row = row + 1
		return True
				
	def isEmpty(self, workingBoard):
		for i in range(RuleSet.rowCount):
			for j in range(RuleSet.colCount):
				if workingBoard[i][j] == SelfState.SHIP:
					return False
		return True

	def sink(self, workingBoard, row, column, ship, direction):
		for k in range(ship):
			workingBoard[row][column] = SelfState.MISS
			if (direction == 0):
				column = column + 1
			else:
				row = row + 1