from .base_bot import BaseBot
import math

class BollingerBot(BaseBot):
    def calculate_sma(self, prices, period):
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def calculate_std(self, prices, period):
        if len(prices) < period:
            return None
        sma = self.calculate_sma(prices, period)
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        return math.sqrt(variance)
    
    def generate_signal(self):
        data = self.get_klines(interval='1h', limit=50)
        if not data or len(data) < 30:
            return None
        
        closes = [k['close'] for k in data]
        current_price = closes[-1]
        
        sma = self.calculate_sma(closes, 20)
        std = self.calculate_std(closes, 20)
        
        if not sma or not std:
            return None
        
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        
        if current_price < lower_band:
            return {'action': 'BUY', 'confidence': 75, 'reason': 'প্রাইস বলিঙ্গার লোয়ার ব্যান্ডের নিচে'}
        elif current_price > upper_band:
            return {'action': 'SELL', 'confidence': 75, 'reason': 'প্রাইস বলিঙ্গার আপার ব্যান্ডের উপরে'}
        else:
            return {'action': 'NEUTRAL', 'confidence': 50, 'reason': 'প্রাইস ব্যান্ডের মধ্যে'}