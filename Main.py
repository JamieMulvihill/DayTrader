from Advanced_Trader import Advanced_Trader
from Performance_Tracker import Performance_Tracker
from Risk_Manager import Risk_Manager
import config
import trade_strat_SMA
import robin_stocks.robinhood as robinhood
import datetime as dt
import time 

def login(days):
        time_logged_in = 60*60*24*days

        try:
            login_response = robinhood.authentication.login(
                username=config.USERNAME,
                password=config.PASSWORD,
                expiresIn=time_logged_in,
                scope='internal',
                by_sms=True,
                store_session=True,
                mfa_code=input("Enter the code you received via SMS: ")
            )
            
            # Check if login was successful
            if login_response:
                print("Successfully logged in")
                return True
            else:
                print("Login failed")
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False

def logout():
        robinhood.authentication.logout()
        print('logged out')


class TradingSystem:
    def __init__(self):
        self.stocks = self.get_stocks() 
        self.trader = Advanced_Trader(self.stocks)
        self.performance = Performance_Tracker()
        self.risk_manager = Risk_Manager()
        self.initial_cash = None

    @staticmethod  # Make this a static method since it doesn't need self
    def get_stocks():
        stocks = list()
        stocks.append('VSAT')
        stocks.append('CETX')
        stocks.append('TSLA')
        return stocks

    def initialize(self):
        if not login(days=6):
            raise Exception("Failed to login")
            self.initial_cash = self.get_cash()[0]
            self.risk_manager.set_daily_limit(self.initial_cash * 0.02)

    def open_market(self):
        market = True
        time_now = dt.datetime.now().time()

        market_open = dt.time(9,30,0)
        market_close = dt.time(15,59,0)

        if time_now > market_open and time_now < market_close:
            market = True
        else:
            print('Market Closed but fake open')

        return market

    def get_cash(self):
        robinhood_cash = robinhood.account.build_user_profile()
        print('Account:', robinhood_cash)

        cash = float(robinhood_cash['cash'])
        equity = float(robinhood_cash['equity'])

        return(cash, equity)

    def get_holdings_and_bought_price(self, stocks):
        holdings = {stocks[i]: 0 for i in range(0, len(stocks))}
        bought_price = {stocks[i]: 0 for i in range(0, len(stocks))}
        robinhood_holdings = robinhood.account.build_holdings()

        for stock in stocks:
            try:
                holdings[stock] = int(float((robinhood_holdings[stock]['quantity'])))
                bought_price[stock] = float((robinhood_holdings[stock]['average_buy_price']))
            except:
                holdings[stock] = 0
                bought_price[stock] = 0

        return(holdings, bought_price)

    def sell(stock, holdings, price):
        sell_price = round((price*.98), 2)
        print('### Trying to SELL {} at ${}'.format(stock, price))

        if stock != 'VSAT':
            print('not a vsat can sell ')
            #sell_order = robinhood.orders.order_sell_limit(symbol = stock, quantity=1, limitPrice=sell_price, timeInForce='gfd')
            

    def buy(stock, allowable_holdings, price):
        buy_price = round((price +.10), 2)
        #buy_order = robinhood.orders.order_buy_limit(symbol = stock, quantity=1, limitPrice=buy_price, timeInForce='gfd')

        print('### Trying to BUY {} at ${}'.format(stock, price))
        
        
    def run(self):
        print('Running')
        self.initialize()
        
        while self.open_market():
            try:
                """ if self.risk_manager.check_daily_limits(self.performance):
                    print("Daily loss limit reached, stopping trading")
                    break """
                    
                prices = robinhood.stocks.get_latest_price(self.trader.stocks)
                holdings, bought_price = self.get_holdings_and_bought_price(self.trader.stocks)
                print("passed the holdings getter")

                for i, stock in enumerate(self.trader.stocks):
                    self.process_single_stock(stock, float(prices[i]), holdings)
                    
                time.sleep(5)
                
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                if "401" in str(e):
                    self.initialize()

    def process_single_stock(self, stock, price, holdings):
        # Check existing positions first
        if holdings[stock] > 0:
            self.manage_existing_position(stock, price, holdings)
            return
            
        # New position entry logic
        if self.trader.analyze_entry(stock, price, self.get_volume(stock)):
            position_size = self.risk_manager.calculate_position_size(
                stock, 
                price, 
                self.get_cash()[0]
            )
            if position_size > 0:
                self.place_new_trade(stock, price, position_size)
    
    def get_volume(self, stock):
        # Add method to get current volume for a stock
        historical = robinhood.stocks.get_stock_historicals(
            stock,
            interval='5minute',
            span='day',
            bounds='regular'
        )
        if historical and len(historical) > 0:
            return float(historical[-1]['volume'])
        return 0
    
    def manage_existing_position(self, stock, price, holdings):
        # Check if we should exit based on profit target or stop loss
        entry_price = self.performance.get_entry_price(stock)
        if entry_price:
            pnl_pct = (price - entry_price) / entry_price
            
            if (pnl_pct >= self.risk_manager.profit_target_pct or 
                pnl_pct <= -self.risk_manager.stop_loss_pct):
                self.exit_position(stock, price, holdings[stock])

    def place_new_trade(self, stock, price, position_size):
        entry, stop, target = self.risk_manager.get_order_prices(price, 'BUY')
        print(f"Placing new trade for {stock}: Entry={entry}, Stop={stop}, Target={target}")
        # Uncomment when ready to trade real money
        # order = robinhood.orders.order_buy_limit(
        #     symbol=stock,
        #     quantity=position_size,
        #     limitPrice=entry,
        #     timeInForce='gfd'
        # )
        self.performance.log_entry(stock, entry, position_size)

    def exit_position(self, stock, price, shares):
        print(f"Exiting position in {stock} at {price}")
        # Uncomment when ready to trade real money
        # order = robinhood.orders.order_sell_limit(
        #     symbol=stock,
        #     quantity=shares,
        #     limitPrice=price,
        #     timeInForce='gfd'
        # )
        self.performance.log_exit(stock, price, shares)
    
def main():
    try:
        trading_system = TradingSystem()
        trading_system.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        logout()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        logout()
    finally:
        logout()

if __name__ == "__main__":
    main()