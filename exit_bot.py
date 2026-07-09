import requests
import math

class ExitBot:
    def __init__(self, symbol):
        self.symbol = symbol
    
    def get_price_data(self):
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={self.symbol}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return float(data['lastPrice'])
        except:
            return None
        return None
    
    def calculate_atr(self, period=14):
        """ATR ক্যালকুলেশন"""
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval=1h&limit={period+1}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                true_ranges = []
                for i in range(1, len(data)):
                    high = float(data[i][2])
                    low = float(data[i][3])
                    prev_close = float(data[i-1][4])
                    tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                    true_ranges.append(tr)
                return sum(true_ranges) / len(true_ranges)
        except:
            pass
        return 0.01  # ডিফল্ট
    
    def get_exit_levels(self, action):
        """টেক প্রফিট ও স্টপ-লস বের করে"""
        price = self.get_price_data()
        if not price:
            return None
        
        atr = self.calculate_atr()
        
        if action == 'BUY':
            tp = price + (atr * 1.5)
            sl = price - (atr * 0.7)
        else:  # SELL
            tp = price - (atr * 1.5)
            sl = price + (atr * 0.7)
        
        risk = abs(price - sl)
        reward = abs(tp - price)
        risk_reward = round(reward / risk, 2) if risk > 0 else 0
        
        return {
            'entry': round(price, 2),
            'tp': round(tp, 2),
            'sl': round(sl, 2),
            'risk_reward': risk_reward,
            'atr': round(atr, 2)
        }