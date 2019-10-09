from playBoard import PlayBoard, Appearance, OpposingState
from boardValidator import BoardValidator
from enemyBoard import BoardInterface
from ruleSet import RuleSet
import subprocess as sp
import importlib
import json
import argparse

# managers interactions with the user as well as the base flow of the game


def printPlayerView(isHuman, playerBoard, enemyBoard):
	if (not isHuman):
		return
	enemyBoard.printOpposingBoard()
	print(str(enemyBoard.activeShips) + " ship pieces remaining")
	print("-------------------------------")
	playerBoard.printSelfBoard()
	print(str(playerBoard.activeShips) + " ship pieces remaining")

def interpretGuess(guess):
	firstChar = guess[0].upper()
	# ascii A is 65 => col 0
	column = ord(firstChar) - 65
	if (column < 0 or column > RuleSet.rowCount - 1):
		raise IOError("INPUT ERROR ON COLUMN " + firstChar)
	secondNum = guess[1:]
	row = int(secondNum) - 1
	if (row < 0 or row > RuleSet.colCount - 1):
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

def performAIGuess(board, aiName):
	boardInterface = BoardInterface(board)
	module = importlib.import_module(aiName)
	class_ = getattr(module, aiName)
	while (not boardInterface.hasGuessBeenMade()):
		# update with reflection to pull other AI names
		try:
			ai = class_(boardInterface)
			ai.makeGuess()
		except IOError as err:
			print("The AI attempted multiple gueses, the first will be the only considered")
		if (not boardInterface.hasGuessBeenMade()):
			print("The AI has failed to make a guess")

def playerAction(p, e):
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
			else:
				guess = interpretGuess(guessedCoordinates)
			
			result = e.guess(guess[0], guess[1])
			# able to complete the input without errors
			break
		except IOError as err:
			print("Error with guess: " + str(err))


def createPlayer(playerNum, playerClass):
	if (playerNum == 1 and not playerClass.upper().endswith("BOT")):
		return None
	try:
		module = importlib.import_module(playerClass)
		class_ = getattr(module, playerClass)	
	except Exception as err:
		print ("player " + str(playerNum) + " did not receive a valid class")
		raise err
	return playerClass

def printIfHuman(isHuman, message):
	if isHuman:
		print (message)

def fetchDefaultConfigs(fileName):
	with open(fileName) as json_file:
		data = json.load(json_file)
		return data

winCount = 0
lossCount = 0

data = fetchDefaultConfigs("config.json")
# init the rule set using config.json
RuleSet(data)

parser = argparse.ArgumentParser()
parser.add_argument('--player1Name', default = None, help='The name of the player (AI names should end with "bot")')
parser.add_argument('--player2Name',  default = None, help='The name of the opposing AI (should end with "bot")')
args = parser.parse_args()

player1Name = None
if (args.player1Name is None):
	player1Name = data['player1Name']
else:
	player1Name = args.player1Name

player1Class = createPlayer(1, player1Name)

player2Name = None
if (args.player2Name is None):
	player2Name = data['player2Name']
else:
	player2Name = args.player2Name

inputBoard = None
if ("inputBoard" in data):
	inputBoard = data["inputBoard"]

player2Class = createPlayer(1, player2Name)


isHuman = (player1Class is None)
for c in range(data["totalGameCount"]):
	e = PlayBoard(None)
	p = PlayBoard(inputBoard)
	validator = BoardValidator(p)
	if (not validator.validate()):
		print("GIVEN BOARD IS NOT VALID")
		quit()
	validator = BoardValidator(e)
	if (not validator.validate()):
		print("OPPOSING BOARD IS NOT VALID, EVALUATE GENERATION LOGIC")
		e.printSelfBoard()
		quit()
	printPlayerView(isHuman ,p, e)
	# main play loop
	while (e.activeShips > 0 and p.activeShips > 0):
		if (isHuman):
			playerAction(p, e)
		else:
			performAIGuess(e, player1Class)

		performAIGuess(p, player2Class)

		if (isHuman):
			sp.call('clear',shell=True)
		if (e.getAppearance(e.lastGuessRow, e.lastGuessCol) == Appearance.MISS):
			printIfHuman(isHuman, "MISS!")
		else:
			printIfHuman(isHuman, "HIT!")
		if (isHuman):
			printPlayerView(isHuman, p, e)
	if (e.activeShips == 0):
		printIfHuman(isHuman, "YOU WIN")
		winCount += 1
	else:
		printIfHuman(isHuman, "YOU LOSE")
		lossCount += 1

print (str(winCount) + " is how much you won")
print (str(lossCount) + " is how much you lost")

# at the end of the game, put down some stats.  Maybe useful.  Should be in a db but overkill is a thing
# analyzing the guesses made by the computer
file=open("postmortem.guess", "a+")
exportGuessHistory(p, file)
# and the board remaining to see which ships survived
file=open("postmortem.board", "a+")
exportBoardHistory(e, file)

