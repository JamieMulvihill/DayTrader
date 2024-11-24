# Trader

import config
import trade_strat_SMA
import robin_stocks.robinhood as robinhood
import datetime as dt
import time 

def login(days):
    time_logged_in = 60*60*24*days
    #print(config.PASSWORD)
    #print(config.USERNAME)
    #robinhood.authentication.login(username=config.USERNAME, password=config.PASSWORD, expiresIn=time_logged_in, scope='internal', by_sms=True, store_session=True)

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

if __name__ == "__main__":
    print('Running')
    if not login(days=6):
        print("Failed to login, exiting")
        exit()
    
    time.sleep(5)  # Add a small delay after login

    stocks = get_stocks()
    print('stocks', stocks)

    ts = trade_strat_SMA.trader(stocks)

    while open_market():
        try:
            prices = robinhood.stocks.get_latest_price(stocks)

            for i, stock in enumerate(stocks):
                price = float(prices[i])
                print('{} = ${}'.format(stock,price))

                #price_data = ts.get_historical_prices(stock, span='day')
                #sma = ts.get_sma(stock, price_data, window=12)
                #print('sma', sma)
                #price_sma = ts.get_price_sma(price, sma)
                #print('price_sma', price_sma)
                # Get historical data using robin_stocks built-in method
                #data = robinhood.stocks.get_stock_historicals(
                    #stock,
                    #interval='5minute',
                    #span='day',
                    #bounds='regular'
                #)
                #if price_data is not None and not price_data.empty: 
                    #print(f"Retrieved {len(price_data)} historical data points for {stock}")
                #else:
                    #print(f"No data or data is empty for {stock}")

                trade = ts.trade_option(stock, price)
                print('trade:', trade)
            time.sleep(15)

        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            # Attempt to re-login if we get an authentication error
            if "401" in str(e):
                print("Attempting to re-authenticate...")
                login(days=6)

