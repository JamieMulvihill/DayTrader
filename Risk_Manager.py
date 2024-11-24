class Risk_Manager:
    def __init__(self):
        self.daily_loss_limit = None
        self.max_position_pct = 0.10  # 10% max per position
        self.stop_loss_pct = 0.002    # 0.2% stop loss
        self.profit_target_pct = 0.003 # 0.3% target
        
    def set_daily_limit(self, limit):
        self.daily_loss_limit = limit
        
    def check_daily_limits(self, performance):
        current_daily_pl = performance.get_daily_pl()
        return current_daily_pl < -self.daily_loss_limit
        
    def calculate_position_size(self, stock, price, current_cash):
        # Calculate based on risk per trade
        daily_risk = current_cash * 0.01  # 1% max risk per day
        position_risk = daily_risk / 4    # Split across multiple trades
        
        max_shares_by_risk = int(position_risk / (price * self.stop_loss_pct))
        max_shares_by_cash = int(current_cash * self.max_position_pct / price)
        
        return min(max_shares_by_risk, max_shares_by_cash)
        
    def get_order_prices(self, price, side):
        if side == 'BUY':
            entry = round(price * 1.001, 2)  # Slightly above ask
            stop = round(price * (1 - self.stop_loss_pct), 2)
            target = round(price * (1 + self.profit_target_pct), 2)
        else:
            entry = round(price * 0.999, 2)  # Slightly below bid
            stop = round(price * (1 + self.stop_loss_pct), 2)
            target = round(price * (1 - self.profit_target_pct), 2)
            
        return entry, stop, target