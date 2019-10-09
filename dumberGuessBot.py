from playBoard import PlayBoard, Appearance
from AbstractAI import AbstractAI
from random import randint
from ruleSet import RuleSet


# given a board, this should provide guesses on where to fire next
class dumberGuessBot(AbstractAI):
	def __init__(self, boardInterface):
		self.boardInterface = boardInterface

	def makeGuess(self):
		for i in range(RuleSet.rowCount):
			for j in range(RuleSet.colCount):
				if (self.boardInterface.getBoardAppearance(i, j) == Appearance.UNKNOWN):
					self.boardInterface.postGuess(i, j)
					return