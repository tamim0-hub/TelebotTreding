from .base_bot import BaseBot

class VolumeBot(BaseBot):
    def generate_signal(self):
        data = self.get_klines(interval='1h', limit=50)
        if not data or len(data) < 30:
            return None
        
        closes = [k['close'] for k in data]
        volumes = [k['volume'] for k in data]
        
        avg_volume = sum(volumes[-24:]) / 24
        current_volume = volumes[-1]
        current_price = closes[-1]
        
        volume_spike = current_volume > (avg_volume * 1.5)
        price_up = current_price > closes[-2]
        
        if volume_spike and price_up:
            return {'action': 'BUY', 'confidence': 70, 'reason': 'ভলিউম স্পাইক + প্রাইস আপ'}
        elif volume_spike and not price_up:
            return {'action': 'SELL', 'confidence': 70, 'reason': 'ভলিউম স্পাইক + প্রাইস ডাউন'}
        else:
            return {'action': 'NEUTRAL', 'confidence': 50, 'reason': 'ভলিউম স্বাভাবিক'}