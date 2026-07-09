from .base_bot import BaseBot

class IchimokuBot(BaseBot):
    def calculate_tenkan(self, prices):
        """Tenkan-sen (Conversion Line)"""
        if len(prices) < 9:
            return None
        return (max(prices[-9:]) + min(prices[-9:])) / 2
    
    def calculate_kijun(self, prices):
        """Kijun-sen (Base Line)"""
        if len(prices) < 26:
            return None
        return (max(prices[-26:]) + min(prices[-26:])) / 2
    
    def generate_signal(self):
        data = self.get_klines(interval='1h', limit=60)
        if not data or len(data) < 40:
            return None
        
        closes = [k['close'] for k in data]
        current_price = closes[-1]
        
        tenkan = self.calculate_tenkan(closes)
        kijun = self.calculate_kijun(closes)
        
        if not tenkan or not kijun:
            return None
        
        # সিগন্যাল
        if tenkan > kijun and current_price > tenkan:
            return {'action': 'BUY', 'confidence': 70, 'reason': 'টেনকান > কিউজুন + প্রাইস উপরে'}
        elif tenkan < kijun and current_price < tenkan:
            return {'action': 'SELL', 'confidence': 70, 'reason': 'টেনকান < কিউজুন + প্রাইস নিচে'}
        else:
            return {'action': 'NEUTRAL', 'confidence': 50, 'reason': 'ক্রসওভার নেই'}