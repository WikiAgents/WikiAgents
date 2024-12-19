```python   
from binance.client import Client
import pandas as pd


@rate_limiter("Binance", max_per_second=1, max_per_minute=10, max_per_hour=1000, timeout=60)
def binance_data(symbol: str, candle_interval: str = "1d", max_results: int = 100):
    """
    Returns crypto currency data from binance.
    
    Args:
        symbol (str): The pair symbol. e.g. BNBBTC or BTCUSDT
        candle_interval (str): The candle interval of the data. e.g. 1m, 5m, 1h, 4h, 1d, 1w, 1M
        max_results (int): The maximum number of results. 
    
    Returns:
        str: The search results
    """
    client = Client()
    candles = client.get_klines(symbol=symbol, interval=candle_interval, limit=max_results)
    df = pd.DataFrame(candles)
    df.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "qav", "number_of_trades", "tbbav", "tbqav", "ignore"]
    return df[["close", "number_of_trades"]].to_dict(orient="list")
```

