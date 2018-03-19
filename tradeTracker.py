
# trade object storing transaction information
class tradeRecord():
    def __init__(self, dateTime, stockCode, companyName, tradeType, units, price, brokerageFee):
        self.dateTime = dateTime
        self.stockCode = stockCode
        self.companyName = companyName
        self.tradeType = tradeType
        self.units = int(units)
        self.price = float(price) # in AUD
        self.brokerageFee = brokerageFee # TODO need to handle 'International Shares'

# stockTrade object used in logs for a specific stock
class stockTrade():
    def __init__(self, dateTime, price, tradeType, units, brokerageFee):
        self.dateTime = dateTime
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
    def __init__(self, dateTime, stockCode, units, aveBuySharePrice, sellPrice, brokerageFee):
        self.dateTime = dateTime
        self.stockCode = stockCode
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

    def calculateBrokerageFee(self, units, price):
        # NOTE: current brokerage values based on trade excecutions on the following type
        # 'Trade online and settle your trade to a CDIA or CommSec Margin Loan'
        transactionValue = int(units) * float(price)
        if transactionValue <= 1000:
            brokerageFee = 10
        elif (transactionValue > 1000) and (transactionValue <= 10000):
            brokerageFee = 19.95
        elif (transactionValue > 10000) and (transactionValue <= 25000):
            brokerageFee = 29.95
        else:
            brokerageFee = 0.0012 * transactionValue

        return brokerageFee

    def addToTradeLog(self, dateTime, stockCode, companyName, tradeType, units, price):
        brokerageFee = self.calculateBrokerageFee(units, price)
        self.tradeLog.append(tradeRecord(dateTime, stockCode, companyName, tradeType, units, price, brokerageFee))
        # print("{}, {}, {}, {}, {}, {}".format(dateTime, stockCode, companyName, tradeType, units, price)) # For debugging

    def updatePortfolio(self):
        # Go through trade log from oldest to newest
        for i in reversed(range(len(tradeLog)-1)):
            trade = tradeLog[i]
            # TODO 

