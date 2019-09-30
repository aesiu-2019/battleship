from playBoard import PlayBoard, Appearance
from random import randint


# given a board, this should provide guesses on where to fire next
class Guesser:
	def __init__(self, playBoard):
		self.activeShips = playBoard.activeShips
		self.board = []
		self.lastHitRow = playBoard.lastHitRow
		self.lastHitCol = playBoard.lastHitCol
		self.battleshipSizes = playBoard.battleshipSizes
		for i in range(PlayBoard.rowCount):
			row = []
			for j in range(PlayBoard.colCount):
				row.append(playBoard.getAppearance(i, j))
			self.board.append(row)

	def initHistory(self, sourceFile):
		self.initHistoryBoards()
		f = open(sourceFile)
		line = f.readline()
		while line:
			entry = line.split(",")
			if (len(entry) != 3):
				line = f.readline()
				continue
			row = int(entry[0])
			col = int(entry[1])
			self.attemptHistory[row][col] += 1
			if ("HIT" in entry[2]):
				self.hitHistory[row][col] += 1
			line = f.readline()

	def getMostSuccessfulOptions(self):
		self.initHistory("postmortem.guess")
		bestOptions = []
		highestSuccess = 0.0
		for i in range(PlayBoard.rowCount):
			for j in range(PlayBoard.colCount):
				if (self.board[i][j] != Appearance.UNKNOWN):
					# not even a possible guess. skip
					continue
				success = self.getSuccessRate(i, j)
				if (success == highestSuccess):
					bestOptions.append([i, j])
				elif (success > highestSuccess):
					highestSuccess = success
					bestOptions = [[i, j]]
		return bestOptions

	def getSuccessRate(self, row, column):
		if (self.attemptHistory[row][column] == 0):
			return 0.5
		return self.hitHistory[row][column] / self.attemptHistory[row][column]

	def initHistoryBoards(self):
		self.attemptHistory = []
		self.hitHistory = []
		for i in range(PlayBoard.rowCount):
			attemptRow = []
			hitRow = []
			for j in range(PlayBoard.colCount):
				attemptRow.append(0.0)
				hitRow.append(0.0)
			self.attemptHistory.append(attemptRow)
			self.hitHistory.append(hitRow)


	def aiGuess(self):
		if (self.activeShips == 0):
			# nothing to guess, might have been a nuke
			return
		# basic rule is to continue attacking ships you found
		continuedOptions = self.getContinuedAssaultOptions()
		if (len(continuedOptions) != 0):
			return continuedOptions[randint(0, len(continuedOptions) - 1)]

		# this is silly but eh
		if (randint(0, 10) == 0):
			# based on previous history, find the most likely place we found a hit in the past and go for it
			mostSuccessfulOptions = self.getMostSuccessfulOptions()
			return mostSuccessfulOptions[randint(0, len(mostSuccessfulOptions) - 1)]

		# otherwise random.  Will probably be the base case forever
		while(True):
			col = randint(0, PlayBoard.rowCount -1)
			row = randint(0, PlayBoard.colCount -1)
			if (self.board[row][col] != Appearance.UNKNOWN):
				continue
			return [row, col]

	def getContinuedAssaultOptions(self):
		row = self.lastHitRow
		col = self.lastHitCol
		if (self.lastHitRow == -1 or self.lastHitCol == -1):
			return []
		returnSet = []
		if (self.getAppearance(row + 1, col) == Appearance.SUNK or self.getAppearance(row - 1, col) == Appearance.SUNK):
			# at least some verticallity, should explore
			# find the beginning of the ship
			startRow = row
			while (self.getAppearance(startRow - 1, col) == Appearance.SUNK):
				startRow -= 1
			# find out how long the current ship is
			endRow = row
			while (self.getAppearance(endRow + 1, col) == Appearance.SUNK):
				endRow += 1
			# silly heuristic but if we've already covered the largest ship there's no point in guessing more
			if (endRow - startRow  + 1 == self.battleshipSizes[0]):
				return []
			
			self.appendIfPotentialHit(startRow - 1, col, returnSet)
			self.appendIfPotentialHit(endRow + 1, col, returnSet)
		if (self.getAppearance(row, col + 1) == Appearance.SUNK or self.getAppearance(row, col - 1) == Appearance.SUNK):
			# at least some horizontality, should explore
			startCol = col
			while (self.getAppearance(row, startCol - 1) == Appearance.SUNK):
				startCol = startCol - 1
			# find out how long the current ship is
			endCol = col
			while (self.getAppearance(row, endCol + 1) == Appearance.SUNK):
				endCol = endCol + 1
			# silly heuristic but if we've already covered the largest ship there's no point in guessing more
			if (endCol - startCol + 1 == self.battleshipSizes[0]):
				return []
			# see if either end is a potential hit
			self.appendIfPotentialHit(row, startCol - 1, returnSet)
			self.appendIfPotentialHit(row, endCol + 1, returnSet)
		
		if (len(returnSet) != 0):
			return returnSet
		# neither vertical or horizontal (yet?).  Could mean a size 1 ship but only if all other blocks are misses
		self.appendIfPotentialHit(row - 1, col, returnSet)
		self.appendIfPotentialHit(row + 1, col, returnSet)
		self.appendIfPotentialHit(row, col -1, returnSet)
		self.appendIfPotentialHit(row, col +1, returnSet)
		return returnSet

	def appendIfPotentialHit(self, row, col, set):
		if (self.getAppearance(row, col) == Appearance.UNKNOWN):
			set.append([row, col])

	def getAppearance(self, row, column):
		if (row > PlayBoard.rowCount - 1 or column > PlayBoard.colCount -1 or row < 0 or column < 0):
			## everything off the border is functionally a miss
			return Appearance.MISS
		return self.board[row][column]
	
	