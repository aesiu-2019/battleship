from playBoard import PlayBoard, Appearance, OpposingState
from boardValidator import BoardValidator
from guesser import Guesser
from enemyBoard import BoardInterface
import subprocess as sp
import importlib

# managers interactions with the user as well as the base flow of the game

def printPlayerView(playerBoard, enemyBoard):
	enemyBoard.printOpposingBoard()
	print(str(enemyBoard.activeShips) + " ship pieces remaining")
	print("-------------------------------")
	playerBoard.printSelfBoard()
	print(str(playerBoard.activeShips) + " ship pieces remaining")

def interpretGuess(guess):
	firstChar = guess[0].upper()
	# ascii A is 65 => col 0
	column = ord(firstChar) - 65
	if (column < 0 or column > PlayBoard.rowCount - 1):
		raise IOError("INPUT ERROR ON COLUMN " + firstChar)
	secondNum = guess[1:]
	row = int(secondNum) - 1
	if (row < 0 or row > PlayBoard.colCount - 1):
		raise IOError("INPUT ERROR ON ROW " + secondNum)
	return [row, column]


def exportBoardHistory(playBoard, file):
		for ship in playBoard.shipsPlaced:
			result = "ALIVE"
			if (playBoard.guessedBoard[ship[0]][ship[1]] == OpposingState.GUESSED):
				result = "HIT"
			file.write(str(ship[0]) + "," + str(ship[1]) + "," + result + "\n")
		file.write("\n")

def exportGuessHistory(playBoard, file):
	for guess in playBoard.guessesMade:
		result = "MISS"
		if (guess[2]):
			result = "HIT"
		file.write(str(guess[0]) + "," + str(guess[1]) + "," + result + "\n")
	file.write("\n")

def performAIGuess(boardInterface):
	while (not boardInterface.hasGuessBeenMade()):
		# update with reflection to pull other AI names
		try:
			module = importlib.import_module("guesser")
			class_ = getattr(module, "Guesser")
			ai = class_(boardInterface)
			ai.makeGuess()
		except IOError as err:
			print("The AI attempted multiple gueses, the first will be the only considered")
		if (not boardInterface.hasGuessBeenMade()):
			print("The AI has failed to make a guess")

e = PlayBoard(None)
p = PlayBoard("input.board")
validator = BoardValidator(p)
if (not validator.validate()):
	print("GIVEN BOARD IS NOT VALID")
	quit()
validator = BoardValidator(e)
if (not validator.validate()):
	print("OPPOSING BOARD IS NOT VALID, EVALUATE GENERATION LOGIC")
	e.printSelfBoard()
	quit()
printPlayerView(p, e)
while (e.activeShips > 0 and p.activeShips > 0):
	result = None
	while result == None:
		try:
			guessedCoordinates = input().upper()
			if (guessedCoordinates == ""):
				continue
			elif (guessedCoordinates == "Q"):
				quit()
			elif (guessedCoordinates == "WIN"):
				e.nuke()
				break
			elif (guessedCoordinates == "LOSE"):
				p.nuke()
				break
			elif (guessedCoordinates == "ANY"):
				# make the AI guess for you
				# TODO: backfill
				pass
			else:
				guess = interpretGuess(guessedCoordinates)
			
			result = e.guess(guess[0], guess[1])
			# able to complete the input without errors
			break
		except IOError as err:
			print("Error with guess: " + str(err))
	boardInterface = BoardInterface(p)
	performAIGuess(boardInterface)

	sp.call('clear',shell=True)
	if (e.getAppearance(e.lastGuessRow, e.lastGuessCol) == Appearance.MISS):
		print("MISS!")
	else:
		print("HIT!")
	printPlayerView(p, e)
if (e.activeShips == 0):
	print("YOU WIN")
else:
	print("YOU LOSE")

# at the end of the game, put down some stats.  Maybe useful.  Should be in a db but overkill is a thing
# analyzing the guesses made by the computer
file=open("postmortem.guess", "a+")
exportGuessHistory(p, file)
# and the board remaining to see which ships survived
file=open("postmortem.board", "a+")
exportBoardHistory(e, file)

