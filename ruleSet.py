
# singleton representing the rules everyone will play with
class RuleSet:

	battleshipSizes = [5, 4, 3, 3, 2]
	rowCount = 10
	colCount = 10

	def __init__(self, data):
		RuleSet.battleshipSizes = data['battleshipSizes'] 
		RuleSet.rowCount = data['rowCount']
		RuleSet.colCount = data['colCount']