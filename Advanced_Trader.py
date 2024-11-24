import pandas as pd
import robin_stocks.robinhood as robinhood

class Advanced_Trader:
    def __init__(self, stocks):
        self.stocks = stocks
        print(stocks)
        # Track multiple timeframes
        self.sma_periods = {'1min': 9, '5min': 20, '15min': 50}
        self.rsi_period = 14
        self.profit_target_pct = 0.003  # 0.3% target per trade
        self.stop_loss_pct = 0.002      # 0.2% stop loss
        
    def analyze_entry(self, stock, price, volume):
        signals = 0
        print("rin analyze_entry")
        # Price trend alignment across timeframes
        for timeframe, period in self.sma_periods.items():
            if price > self.calculate_sma(stock, timeframe, period):
                signals += 1
                
        # Volume confirmation
        avg_volume = self.get_average_volume(stock, '5min')
        if volume > avg_volume * 1.2:  # 20% above average
            signals += 1
            
        # RSI confirmation
        rsi = self.calculate_rsi(stock)
        if 30 <= rsi <= 70:  # Not overbought/oversold
            signals += 1
            
        return signals >= 4  # Require multiple confirmations
    
    def calculate_rsi(self, stock):
        """Calculate the RSI for the given stock."""
        
        # Get the historical prices
        df = self.get_historical_prices(stock, span="5min")  # You can adjust span here
        
        if df is None:
            return None

        # Calculate the price changes
        delta = df['close_price'].diff()
        
        # Separate the gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate the average gain and average loss over the period (14 by default)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        
        # Avoid division by zero
        rs = avg_gain / avg_loss
        rs = rs.fillna(0)  # Fill any NaN values resulting from division by zero
        
        # Calculate the RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]  # Return the latest RSI value
    
    def get_historical_prices(self, stock, span):
        # Define interval mappings based on timeframe
        span_interval = {'1min': '5minute', '5min': '10minute', '15min': '15minute'}
        interval = span_interval.get(span, '5minute')  # Default to '5minute' if not found

        # Get historical data from Robinhood
        data = robinhood.stocks.get_stock_historicals(
            stock,
            interval=interval,
            span='day',  # Adjust this as necessary
            bounds='regular'
        )

        if data and isinstance(data, list):  # Check if data is a list
            print(f"Type of data: {type(data)}")  # Debug print to check type
            
            # Inspect the first entry to check for volume
            if 'volume' not in data[0]:
                print("Warning: 'volume' not found in historical data")
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

        # Return None if no valid data is returned
        print("Error: No valid data received.")
        return None

    def get_average_volume(self, stock, timeframe='5min', period=20):
        # Get historical prices for the stock using the given timeframe
        df_prices = self.get_historical_prices(stock, timeframe)
        
        if df_prices is not None and not df_prices.empty:
            # Calculate the average volume for the given period
            avg_volume = df_prices['volume'].rolling(window=period).mean().iloc[-1]
            return avg_volume
        return 0  # Return 0 if no data is available

    def calculate_sma(self, stock, timeframe, period):
         # Get historical prices for the stock and timeframe
        df_prices = self.get_historical_prices(stock, span='day')  # 'span' could vary based on timeframe or context

        # Check if the DataFrame is valid and contains data
        if df_prices is not None and not df_prices.empty:
            # Calculate the SMA using the period (window size) provided
            print(f"Calculating SMA for {stock} using timeframe: {timeframe} and period: {period}")

            # Use the 'close_price' column to calculate the SMA for the specified period
            sma = df_prices['close_price'].rolling(window=period, min_periods=1).mean()

            # Get the latest SMA value and return it rounded
            return round(sma.iloc[-1], 4)
        
        # Return None if data is invalid or not found
        return None
    
    def get_price_sma(self, price, sma):
        price_sma = round(price/sma, 4)
        print('Price_sma:', price_sma)
        return price_sma
    
    def trade_option(self, stock, price):
        if self.run_time % 5 == 0:
            df_historical_prices = self.get_historical_prices(stock, span='day')

             # Print if the data is None or valid
            if df_historical_prices is None:
                print(f"Warning: Historical prices for {stock} returned None.")
            else:
                print(f"Successfully retrieved historical data for {stock}:")
                print(df_historical_prices.head())  # Display the first few rows of the data for checking

            if df_historical_prices is not None:
                self.sma_hour[stock] = self.calculate_sma(stock, df_historical_prices, window=12)

            #self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-12:], window=12)

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