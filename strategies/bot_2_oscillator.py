from .base_bot import BaseBot

class OscillatorBot(BaseBot):
    def calculate_rsi(self, closes, period=14):
        """RSI ক্যালকুলেশন"""
        if len(closes) < period + 1:
            return 50
        
        gains = 0
        losses = 0
        for i in range(1, period + 1):
            diff = closes[-i] - closes[-i-1]
            if diff > 0:
                gains += diff
            else:
                losses += abs(diff)
        
        if losses == 0:
            return 100
        rs = gains / losses
        return 100 - (100 / (1 + rs))
    
    def generate_signal(self):
        data = self.get_klines(interval='1h', limit=50)
        if not data or len(data) < 30:
            return None
        
        closes = [k['close'] for k in data]
        rsi = self.calculate_rsi(closes, 14)
        
        if rsi < 30:
            return {'action': 'BUY', 'confidence': 80, 'reason': f'RSI: {rsi:.1f} (ওভারসল্ড)'}
        elif rsi > 70:
            return {'action': 'SELL', 'confidence': 80, 'reason': f'RSI: {rsi:.1f} (ওভারবট)'}
        else:
            return {'action': 'NEUTRAL', 'confidence': 50, 'reason': f'RSI: {rsi:.1f} (নিউট্রাল)'}