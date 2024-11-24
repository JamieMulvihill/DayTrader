# Trader

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

def get_stocks():
    stocks = list()
    stocks.append('VSAT')
    stocks.append('CETX')
    stocks.append('TSLA')
    
    return(stocks)

def open_market():
    market = True
    time_now = dt.datetime.now().time()

    market_open = dt.time(9,30,0)
    market_close = dt.time(15,59,0)

    if time_now > market_open and time_now < market_close:
        market = True
    else:
        print('Market Closed')

    return market

def get_historical_prices(self, stock, span):
    try:
        # Use robin_stocks built-in historical data method instead
        historical_data = robinhood.stocks.get_stock_historicals(
            stock,
            interval='5minute',
            span='day',
            bounds='regular'
        )
        
        if historical_data:
            print(f"Successfully retrieved historical data for {stock}")
            return historical_data
        else:
            print(f"No historical data received for {stock}")
            return None
            
    except Exception as e:
        print(f"Error getting historical data for {stock}: {str(e)}")
        return None

def get_cash():
    robinhood_cash = robinhood.account.build_user_profile()
    print('Account:', robinhood_cash)

    cash = float(robinhood_cash['cash'])
    equity = float(robinhood_cash['equity'])

    return(cash, equity)

def get_holdings_and_bought_price(stocks):
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
        sell_order = robinhood.orders.order_sell_limit(symbol = stock, quantity=1, limitPrice=sell_price, timeInForce='gfd')
        

def buy(stock, allowable_holdings):
    buy_price = round((price +.10), 2)
    buy_order = robinhood.orders.order_buy_limit(symbol = stock, quantity=1, limitPrice=buy_price, timeInForce='gfd')

    print('### Trying to BUY {} at ${}'.format(stock, price))

if __name__ == "__main__":
    print('Running')
    if not login(days=6):
        print("Failed to login, exiting")
        exit()
    
    time.sleep(5)  # Add a small delay after login

    stocks = get_stocks()
    print('stocks', stocks)

    cash, equity = get_cash()

    ts = trade_strat_SMA.trader(stocks)

    while open_market():
        try:
            prices = robinhood.stocks.get_latest_price(stocks)
            holdings, bought_price = get_holdings_and_bought_price(stocks)
            print('holdings:', holdings)
            print('bought_price:', bought_price)

            for i, stock in enumerate(stocks):
                price = float(prices[i])
                print('{} = ${}'.format(stock,price))

                trade = ts.trade_option(stock, price)
                print('trade:', trade)

                if trade == 'BUY':
                    allowable_holdings = int((cash/10)/price)
                    if allowable_holdings > 5 and holdings[stock] == 0:
                        buy(stock, allowable_holdings)
                elif trade == 'SELL':
                    if holdings[stock] > 0:
                        sell(stock, holdings, price)


            time.sleep(15)

        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            # Attempt to re-login if we get an authentication error
            if "401" in str(e):
                print("Attempting to re-authenticate...")
                login(days=6)

