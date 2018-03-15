
# trade object storing transaction information
class trade():
	def __init__(self, date, code, companyName, tradeType, units, price, brokerageFee):
		self.date = date
		self.code = code
		self.companyName = companyName
		self.tradeType = tradeType
		self.units = units
		self.price = price # in AUD
		self.brokerageFee = brokerageFee # TODO need to handle 'International Shares'

# stockTrade object used in logs for a specific stock
class stockTrade():
	def __init__(self, date, price, tradeType, units, brokerageFee):
		self.date = date
		self.price = price
		self.units = units
		self.brokerageFee = brokerageFee

# heldStock object storing current status of a stock held in portfolio
class heldStock():
	def __init__(self, companyName, unitsHeld=0, aveSharePrice=0):
		self.companyName = companyName
		self.unitsHeld = unitsHeld
		self.aveSharePrice = aveSharePrice
		self.stockTradeLog = []

# object used in tradeSummary for recording sell transaction
class sellTransaction():
	def __init__(self, date, code, units, aveBuySharePrice, sellPrice, brokerageFee):
		self.date = date
		self.code = code
		self.units = units
		self.aveBuySharePrice = aveBuySharePrice
		self.sellPrice = sellPrice
		self.PL = (sellPrice - aveBuySharePrice) * units
		self.brokerageFee = brokerageFee

# tradeSummary object storing transactions of sold stocks and trading summary
# NOTE: PL stands for profit/loss
class tradeSummary():
	def __init__(self):
		self.grossTotalRealisedPL = 0 # before taking into account brokerage fees
		self.grossTotalPaperPL = 0 # TODO later using stock price API from somewhere
		self.totalBrokerageFees = 0
		self.sellTransactions = [] # List of sellTransaction objects

# Main module handling all the trade information
class tradeTracker():
    def __init__(self):
    	self.tradeLog = [] # List of trade objects
    	self.portfolio = {} # Dict of heldStock objects with stockCode as dict key
    	self.summary = tradeSummary()

    def addToTradeLog(self, date, code, companyName, tradeType, units, price, brokerageFee):
    	self.tradeLog.append(trade(date, code, companyName, tradeType, units, price, brokerageFee))



    # information I need
    # - Subject for getting the 'stock code'
    # - Message body for getting the 'units', 'BOUGHT/SOLD', 'price'
    # - Make a function to calc brokerage fee 

