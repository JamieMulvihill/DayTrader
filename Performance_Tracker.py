import datetime as dt

class Performance_Tracker:
    def __init__(self):
        self.trades = []
        self.daily_stats = {}
        
    def log_trade(self, stock, entry_price, exit_price, shares, timestamp):
        profit_loss = (exit_price - entry_price) * shares
        profit_loss_pct = (exit_price - entry_price) / entry_price
        
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
        # Iterate through trades to find the entry price for the given stock
        for trade in self.trades:
            if trade['stock'] == stock and trade['exit'] == 0:  # Assuming exit=0 means open position
                return trade['entry']
        return None  # Return None if no open position is found for the stock