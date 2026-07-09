from strategies.bot_1_trend import TrendBot
from strategies.bot_2_oscillator import OscillatorBot
from strategies.bot_3_volume import VolumeBot
from strategies.bot_4_macd import MACDBot
from strategies.bot_5_bollinger import BollingerBot
from strategies.bot_6_ichimoku import IchimokuBot
from exit_bot import ExitBot
from config import SIGNAL_THRESHOLD
from datetime import datetime

class Orchestrator:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bots = {
            'Trend': TrendBot(symbol),
            'Oscillator': OscillatorBot(symbol),
            'Volume': VolumeBot(symbol),
            'MACD': MACDBot(symbol),
            'Bollinger': BollingerBot(symbol),
            'Ichimoku': IchimokuBot(symbol)
        }
        self.exit_bot = ExitBot(symbol)
    
    def get_consensus(self):
        """স্কোর ভিত্তিক সিগন্যাল জেনারেশন"""
        signals = {}
        buy_score = 0
        sell_score = 0
        total_bots = 0
        
        for name, bot in self.bots.items():
            try:
                signal = bot.generate_signal()
                if signal:
                    signals[name] = signal
                    confidence = signal.get('confidence', 50)
                    if signal['action'] == 'BUY':
                        buy_score += confidence
                    elif signal['action'] == 'SELL':
                        sell_score += confidence
                    total_bots += 1
            except Exception as e:
                print(f"⚠️ {name} বটে এরর: {e}")
        
        if not signals or total_bots == 0:
            return None
        
        # গড় স্কোর
        avg_buy = buy_score / total_bots
        avg_sell = sell_score / total_bots
        
        # সিগন্যাল নির্ধারণ
        if avg_buy > SIGNAL_THRESHOLD and avg_buy > avg_sell:
            action = 'BUY'
            confidence = round((avg_buy / 100) * 100, 1)
            consensus_count = len([s for s in signals.values() if s['action'] == 'BUY'])
        elif avg_sell > SIGNAL_THRESHOLD and avg_sell > avg_buy:
            action = 'SELL'
            confidence = round((avg_sell / 100) * 100, 1)
            consensus_count = len([s for s in signals.values() if s['action'] == 'SELL'])
        else:
            action = 'NEUTRAL'
            confidence = round((max(avg_buy, avg_sell) / 100) * 100, 1)
            consensus_count = len([s for s in signals.values() if s['action'] != 'NEUTRAL'])
        
        exit_data = self.exit_bot.get_exit_levels(action) if action in ['BUY', 'SELL'] else None
        
        return {
            'symbol': self.symbol,
            'action': action,
            'confidence': min(95, confidence),
            'consensus_count': consensus_count,
            'total_bots': total_bots,
            'signals': signals,
            'exit': exit_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'score': {
                'buy': round(avg_buy, 1),
                'sell': round(avg_sell, 1)
            }
        }