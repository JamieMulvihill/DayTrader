import datetime as dt

class Performance_Tracker:
    def __init__(self):
        self.trades = []
        self.daily_stats = {}
        self.positions = {}  # Dictionary to track open positions
        
    def log_trade(self, stock, entry_price, exit_price, shares, timestamp):
        print(f"Logging trade for {stock} at entry price: {entry_price} and exit price: {exit_price}")
        profit_loss = (exit_price - entry_price) * shares
        profit_loss_pct = (exit_price - entry_price) / entry_price
        
        # If exit price is zero, it's an open position; log the entry price in positions
        if exit_price == 0:
            self.positions[stock] = entry_price  # Track open positions by stock
        else:
            trade = {
                'stock': stock,
                'entry': entry_price,
                'exit': exit_price,
                'shares': shares,
                'pl': profit_loss,
                'pl_pct': profit_loss_pct,
                'timestamp': timestamp
            }
            self.trades.append(trade)
            self.update_daily_stats(trade)
            if stock in self.positions:
                del self.positions[stock]  # Remove position after exit

    def update_daily_stats(self, trade):
        date = trade['timestamp'].date()
        if date not in self.daily_stats:
            self.daily_stats[date] = {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'total_pl': 0
            }
        
        stats = self.daily_stats[date]
        stats['trades'] += 1
        stats['total_pl'] += trade['pl']
        if trade['pl'] > 0:
            stats['wins'] += 1
        else:
            stats['losses'] += 1

    def get_daily_pl(self, date=None):
        if date is None:
            date = dt.datetime.now().date()  # Default to today's date
        
        # Return the total P&L for the given date
        daily_stats = self.daily_stats.get(date, None)
        if daily_stats:
            return daily_stats['total_pl']
        else:
            return 0  # Return 0 if no trades were made for the given date
        
    def get_entry_price(self, stock):
        print(f"Checking entry price for {stock}")
        # If the stock is in positions, it means it is an open position
        if stock in self.positions:
            print(f"Found entry price for open position: {self.positions[stock]} for {stock}")
            return self.positions[stock]
        
        # Otherwise, search through closed trades
        for trade in self.trades:
            if trade['stock'] == stock and trade['exit'] != 0:  # Trade with an exit
                print(f"Found entry price: {trade['entry']} for {stock}")
                return trade['entry']
        
        print(f"Entry price for {stock} not found in trades or positions.")
        return None  # Return None if no position is found for the stock