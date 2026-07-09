from .base_bot import BaseBot

class MACDBot(BaseBot):
    def calculate_ema(self, prices, period):
        if len(prices) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def generate_signal(self):
        data = self.get_klines(interval='1h', limit=100)
        if not data or len(data) < 60:
            return None
        
        closes = [k['close'] for k in data]
        ema_12 = self.calculate_ema(closes, 12)
        ema_26 = self.calculate_ema(closes, 26)
        
        if not ema_12 or not ema_26:
            return None
        
        macd = ema_12 - ema_26
        
        # সরল সিগন্যাল
        if macd > 0 and closes[-1] > closes[-2]:
            return {'action': 'BUY', 'confidence': 70, 'reason': f'MACD: {macd:.2f} (পজিটিভ)'}
        elif macd < 0 and closes[-1] < closes[-2]:
            return {'action': 'SELL', 'confidence': 70, 'reason': f'MACD: {macd:.2f} (নেগেটিভ)'}
        else:
            return {'action': 'NEUTRAL', 'confidence': 50, 'reason': f'MACD: {macd:.2f} (নিউট্রাল)'}