# Trader

import config
import robin_stocks.robinhood as robinhood
import datetime as dt
import time 

def login(days):
    time_logged_in = 60*60*24*days
    print(config.PASSWORD)
    print(config.USERNAME)
    robinhood.authentication.login(username=config.USERNAME, password=config.PASSWORD, expiresIn=time_logged_in, scope='internal', by_sms=True, store_session=True)

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

if __name__ == "__main__":
    print('Running')
    login(days=1)

    stocks = get_stocks()
    print('stocks', stocks)

    while open_market():
        prices = robinhood.stocks.get_latest_price(stocks)
        print('prices', prices)


        time.sleep(15)