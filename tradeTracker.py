
# trade object storing transaction information
class tradeRecord():
    def __init__(self, dateTime, stockCode, companyName, tradeType, units, price, brokerageFee):
        self.dateTime = dateTime
        self.stockCode = stockCode
        self.companyName = companyName
        self.tradeType = tradeType # Either BOUGHT or SOLD
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
    def __init__(self, companyName, units=0, aveBuySharePrice=0):
        self.companyName = companyName
        self.units = units # Units held
        self.aveBuySharePrice = aveBuySharePrice
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

    def updatePortfolioAndSummary(self):
        # Go through trade log from oldest to newest
        # for i in reversed(range(len(self.tradeLog))): # No need to reverse anymore since
        for i in range(len(self.tradeLog)):
            t = self.tradeLog[i]

            # Check if buy or sell
            if t.tradeType == "BOUGHT":
                if t.stockCode not in self.portfolio:
                    self.portfolio[t.stockCode] = heldStock(t.companyName, t.units, t.price)
                else:
                    currS = self.portfolio[t.stockCode]
                    self.portfolio[t.stockCode].aveBuySharePrice = ( (t.price * t.units) + (currS.aveBuySharePrice * currS.units) ) / (t.units + currS.units)
                    self.portfolio[t.stockCode].units += t.units
                # Add to transaction history for that stock
                self.portfolio[t.stockCode].stockTradeLog.append(stockTrade(t.dateTime, t.price, t.tradeType, t.units, t.brokerageFee))

                # Step 2: Update trade summary
                self.summary.totalBrokerageFees += t.brokerageFee

            if t.tradeType == "SOLD":
                # TODO handle edge case of selling a stock not in Dict or empty
                if t.stockCode not in self.portfolio:

                    print("Date: {}, Stock: {}".format(t.dateTime, t.stockCode))
            
                    print("NANI?!") # Perhaps was a rights issue or IPO?, maybe need a prompt for entering bought price here
                    exit()
                else:
                    # Step 1: Update portfolio

                    # Need an edge case where there was not email for buying the share, e.g. BUB new share issue
                    if self.portfolio[t.stockCode].units == 0:
                        correctTypeFlag = False
                        while not correctTypeFlag:
                            try:
                                aveBuySharePrice = float(input("     Please enter missing information (Share buy price for {}): ".format(t.stockCode)))
                                correctTypeFlag = True
                            except ValueError as e:
                                print("     ! -- Warning -- ! value entered was not a number, please try again")
                    else:
                        self.portfolio[t.stockCode].units -= t.units
                        aveBuySharePrice = self.portfolio[t.stockCode].aveBuySharePrice

                # Add to transaction history for that stock
                self.portfolio[t.stockCode].stockTradeLog.append(stockTrade(t.dateTime, t.price, t.tradeType, t.units, t.brokerageFee))

                # Step 2: Update trade summary
                self.summary.totalBrokerageFees += t.brokerageFee
                self.summary.sellTransactions.append(sellTransaction(t.dateTime, t.stockCode, t.units, aveBuySharePrice, t.price, t.brokerageFee))

    def prettyPrintNumber(self, n):
        n = round(float(n), 2)
        n = "{:,}".format(n) #Add comma at tens, hunders, etc. mark
        return n

    def printSummary(self):
        self.grossTotalRealisedPL = 0 # Reset to 0
        for s in self.summary.sellTransactions:
            self.grossTotalRealisedPL += s.PL

        print("Total GROSS realised P/L: ${}".format(self.prettyPrintNumber(self.grossTotalRealisedPL))) # TODO over specified period
        print("Total brokerageFees:      ${}".format(self.prettyPrintNumber(self.summary.totalBrokerageFees)))
        print("Total NET realised P/L:   ${}".format(self.prettyPrintNumber(self.grossTotalRealisedPL - self.summary.totalBrokerageFees)))