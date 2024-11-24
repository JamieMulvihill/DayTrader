import pandas as pd
import robin_stocks.robinhood as robinhood


class trader():
    def __init__(self, stocks):
        self.stocks = stocks

        self.sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}
        self.run_time = 0
        self.buffer = 0.005

        self.price_sma_hour = {stocks[i]: 0 for i in range(0, len(stocks))}

    def get_historical_prices(self, stock, span):
        span_interval = {'day': '5minute', 'week': '10minute', 'month': 'hour', '3month': 'hour', 'year': 'day', '5year': 'week'}
        interval = span_interval[span]

        data = robinhood.stocks.get_stock_historicals(
            stock,
            interval=interval,
            span=span,
            bounds='regular'
            )   

        if data is not None and len(data) > 0: 
            df = pd.DataFrame(data)

            date_times = pd.to_datetime(df.loc[:, 'begins_at'])
            close_prices = df.loc[:,'close_price'].astype('float')

            df_price = pd.concat([close_prices, date_times], axis=1)
            df_price = df_price.rename(columns={'close_price': stock})
            df_price = df_price.set_index('begins_at')

            return df_price
        
        return None


    def get_sma(self, stock, df_prices, window=12):
        sma = df_prices.rolling(window=window, min_periods=window).mean()
        sma = round(float(sma[stock].iloc[-1]), 4)
        return sma
    
    def get_price_sma(self, price, sma):
        price_sma = round(price/sma, 4)
        print('Price_sma:', price_sma)
        return price_sma
    
    def trade_option(self, stock, price):
        if self.run_time % 5 == 0:
            df_historical_prices = self.get_historical_prices(stock, span='day')
            self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-12:], window=12)

        self.price_sma_hour[stock] = self.get_price_sma(price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]

        indicator = "BUY" if self.price_sma_hour[stock] < 1.0 else "SELL" if self.price_sma_hour[stock] > 1.0 else "NONE"

        if indicator == "BUY":
            trade = "BUY"
        elif indicator == "SELL":
            trade = "SELL"
        else:
            trade = "HOLD"

        return trade