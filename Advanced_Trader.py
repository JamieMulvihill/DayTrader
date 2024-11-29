import pandas as pd
import robin_stocks.robinhood as robinhood
import yfinance as yf

class Advanced_Trader:
    def __init__(self, stocks):
        self.stock_universe = self.get_sp500_tickers()
        self.stocks = self.stock_universe
        print(f"Stocks to track: {stocks}")
        # Track multiple timeframes
        self.sma_periods = {'5minute': 20, '15minute': 50, '1hour': 100}
        self.rsi_period = 14
        self.profit_target_pct = 0.003  # 0.3% target per trade
        self.stop_loss_pct = 0.002      # 0.2% stop loss

    def analyze_entry(self, stock, price, volume):
        signals = 0
        print("Analyzing entry for stock:", stock)
        
        # Price trend alignment across timeframes
        for timeframe, period in self.sma_periods.items():
            sma = self.calculate_sma(stock, timeframe, period)
            if sma is not None and price > sma:
                signals += 1
                print(f"SMA signal for {timeframe} timeframe: {sma}")
            else:
                print(f"Failed SMA for {timeframe} timeframe: price {price} <= SMA {sma}")

        # Volume confirmation
        avg_volume = self.get_average_volume(stock, '5minute')
        if volume > avg_volume * 1.2:  # 20% above average
            signals += 1
            print(f"Volume confirmation for {stock}: {volume} > {avg_volume * 1.2}")
        else:
            print(f"Failed volume confirmation for {stock}: volume {volume} <= {avg_volume * 1.2}")

        # RSI confirmation
        rsi = self.calculate_rsi(stock)
        if rsi and 30 <= rsi <= 70:  # Not overbought/oversold
            signals += 1
            print(f"RSI confirmation for {stock}: {rsi}")

        # Return True if at least 4 signals are confirmed
        print(f"Total signals: {signals}")
        return signals >= 4

    def calculate_rsi(self, stock):
        """Calculate the RSI for the given stock."""
        print(f"Calculating RSI for {stock}")
        df = self.get_historical_prices(stock, span="5minute")  # Adjust span as needed

        print("len in calrsi")
        if df is None or len(df) < self.rsi_period:
            print(f"Error: Not enough data to calculate RSI for {stock}")
            return None

        # Calculate the price changes
        delta = df['close_price'].diff()

        # Separate the gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Calculate the average gain and average loss over the period
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()

        # Avoid division by zero
        rs = avg_gain / avg_loss
        rs = rs.fillna(0)  # Fill NaN values resulting from division by zero

        # Calculate the RSI
        rsi = 100 - (100 / (1 + rs))
        print(f"RSI for {stock}: {rsi.iloc[-1]}")

        return rsi.iloc[-1]  # Return the latest RSI value

    def get_historical_prices(self, stock, span):
        # Define interval mappings based on timeframe
        span_interval = {'5minute': '5minute', '10minute': '10minute', 'day': 'day'}
        interval = span_interval.get(span, '5minute')  # Default to '5minute' if not found

        print(f"Using interval: {interval} for timeframe: {span}")  # Debug print to check interval

        # Get historical data from Robinhood
        try:
            data = robinhood.stocks.get_stock_historicals(
                stock,
                interval=interval,
                span='day',  # Adjust this as necessary for the historical range (could be 'day', 'week', etc.)
                bounds='regular'
            )
        except Exception as e:
            print(f"Error fetching historical data for {stock}: {e}")
            return None

        if data and isinstance(data, list):  # Check if data is a list
            if 'volume' not in data[0]:
                print("Warning: 'volume' not found in historical data for", stock)
                return None

            # Convert list of dictionaries to DataFrame
            df = pd.DataFrame(data)

            # Convert 'begins_at' to datetime and 'close_price' to float
            df['begins_at'] = pd.to_datetime(df['begins_at'])
            df['close_price'] = df['close_price'].astype(float)
            df['volume'] = df['volume'].astype(float)  # Ensure volume is a float

            # Set 'begins_at' as index
            df.set_index('begins_at', inplace=True)

            return df[['close_price', 'volume']]  # Return 'close_price' and 'volume' columns

        print(f"Error: No valid data received for {stock}.")
        return None

    def get_average_volume(self, stock, timeframe='5minute', period=20):
        # Get historical prices for the stock using the given timeframe
        df_prices = self.get_historical_prices(stock, timeframe)

        if df_prices is not None and not df_prices.empty:
            # Calculate the average volume for the given period
            avg_volume = df_prices['volume'].rolling(window=period).mean().iloc[-1]
            print(f"Average volume for {stock}: {avg_volume}")
            return avg_volume
        return 0  # Return 0 if no data is available

    def calculate_sma(self, stock, timeframe, period):
        # Get historical prices for the stock using the correct timeframe
        df_prices = self.get_historical_prices(stock, span=timeframe)

        # Check if the DataFrame is valid and contains data
        if df_prices is not None and not df_prices.empty:
            print(f"Calculating SMA for {stock} using timeframe: {timeframe} and period: {period}")
            # Calculate the SMA using the period (window size) provided
            sma = df_prices['close_price'].rolling(window=period, min_periods=1).mean()

            # Get the latest SMA value and return it rounded
            return round(sma.iloc[-1], 4)

        # Return None if data is invalid or not found
        return None
    
    def get_price_sma(self, price, sma):
        price_sma = round(price/sma, 4)
        print(f"Price to SMA ratio: {price_sma}")
        return price_sma

    def trade_option(self, stock, price):
        # Get historical prices for the stock
        df_historical_prices = self.get_historical_prices(stock, span='day')

        if df_historical_prices is None:
            print(f"Warning: Historical prices for {stock} returned None.")
            return "HOLD"

        # Calculate SMA for the stock
        sma = self.calculate_sma(stock, timeframe='day', period=12)

        if sma is None:
            print(f"SMA calculation failed for {stock}.")
            return "HOLD"  # If SMA is None, hold the trade

        # Calculate price relative to SMA
        price_sma = self.get_price_sma(price, sma)
        print(f"Price to SMA ratio for {stock}: {price_sma}")

        # Decide whether to buy, sell, or hold based on the price-to-SMA ratio
        if price_sma < 1.0:
            trade = "BUY"
        elif price_sma > 1.0:
            trade = "SELL"
        else:
            trade = "HOLD"

        return trade

    # Example: Fetch all stocks in the S&P 500
    def get_sp500_tickers(self):
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500_df = tables[0]
        tickers = sp500_df['Symbol'].tolist()
        return tickers

    # Fetch stock data for all tickers
    def get_stock_data(self, tickers):
        data = {}
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            data[ticker] = stock.history(period="1d")  # or other period
        return data