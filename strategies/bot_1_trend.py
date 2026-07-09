from .base_bot import BaseBot

class TrendBot(BaseBot):
    def calculate_ema(self, prices, period):
        """এক্সপোনেনশিয়াল মুভিং এভারেজ ক্যালকুলেশন"""
        if len(prices) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def generate_signal(self):
        data = self.get_klines(interval='1h', limit=200)
        if not data or len(data) < 200:
            return None
        
        closes = [k['close'] for k in data]
        ema_50 = self.calculate_ema(closes, 50)
        ema_200 = self.calculate_ema(closes, 200)
        
        if not ema_50 or not ema_200:
            return None
        
        current_price = closes[-1]
        
        # ট্রেন্ড সিগন্যাল
        if ema_50 > ema_200 and current_price > ema_50:
            return {'action': 'BUY', 'confidence': 75, 'reason': 'EMA ৫০ > EMA ২০০, আপট্রেন্ড'}
        elif ema_50 < ema_200 and current_price < ema_50:
            return {'action': 'SELL', 'confidence': 75, 'reason': 'EMA ৫০ < EMA ২০০, ডাউনট্রেন্ড'}
        else:
            return {'action': 'NEUTRAL', 'confidence': 50, 'reason': 'কোনো স্পষ্ট ট্রেন্ড নেই'}