import requests
from abc import ABC, abstractmethod

class BaseBot(ABC):
    def __init__(self, symbol):
        self.symbol = symbol
    
    def get_price_data(self):
        """Binance পাবলিক API থেকে ডেটা আনে"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={self.symbol}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'price': float(data['lastPrice']),
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume']),
                    'change': float(data['priceChangePercent'])
                }
        except Exception as e:
            print(f"⚠️ {self.symbol} ডেটা আনতে ব্যর্থ: {e}")
        return None
    
    def get_klines(self, interval='1h', limit=100):
        """ক্যান্ডেলস্টিক ডেটা আনে"""
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval={interval}&limit={limit}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [{
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5])
                } for k in data]
        except Exception as e:
            print(f"⚠️ {self.symbol} ক্যান্ডেল ডেটা আনতে ব্যর্থ: {e}")
        return []
    
    @abstractmethod
    def generate_signal(self):
        """প্রত্যেক বটকে এই মেথড ইমপ্লিমেন্ট করতে হবে"""
        pass