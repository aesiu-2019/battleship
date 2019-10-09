from playBoard import PlayBoard, Appearance
from AbstractAI import AbstractAI
from random import randint


# given a board, this should provide guesses on where to fire next
class dumberGuessBot(AbstractAI):
	def __init__(self, boardInterface):
		self.boardInterface = boardInterface

	def makeGuess(self):
		for i in range(PlayBoard.rowCount):
			for j in range(PlayBoard.colCount):
				if (self.boardInterface.getBoardAppearance(i, j) == Appearance.UNKNOWN):
					self.boardInterface.postGuess(i, j)
					return