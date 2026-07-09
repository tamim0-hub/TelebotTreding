from strategies.bot_1_trend import TrendBot
from strategies.bot_2_oscillator import OscillatorBot
from strategies.bot_3_volume import VolumeBot
from strategies.bot_4_macd import MACDBot
from strategies.bot_5_bollinger import BollingerBot
from strategies.bot_6_ichimoku import IchimokuBot
from exit_bot import ExitBot
from config import CONSENSUS_THRESHOLD
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
        """সব বট থেকে সিগন্যাল সংগ্রহ করে কনসেনসাস তৈরি করে"""
        signals = {}
        for name, bot in self.bots.items():
            try:
                signal = bot.generate_signal()
                if signal:
                    signals[name] = signal
            except Exception as e:
                print(f"⚠️ {name} বটে এরর: {e}")
        
        # BUY/SELL এর সংখ্যা গণনা
        buy_count = sum(1 for s in signals.values() if s.get('action') == 'BUY')
        sell_count = sum(1 for s in signals.values() if s.get('action') == 'SELL')
        
        # কনসেনসাস চেক
        if buy_count >= CONSENSUS_THRESHOLD:
            action = 'BUY'
            confidence = (buy_count / len(self.bots)) * 100
        elif sell_count >= CONSENSUS_THRESHOLD:
            action = 'SELL'
            confidence = (sell_count / len(self.bots)) * 100
        else:
            return None  # কোনো কনসেনসাস নেই
        
        # এক্সিট স্ট্র্যাটেজি
        exit_data = self.exit_bot.get_exit_levels(action)
        
        return {
            'symbol': self.symbol,
            'action': action,
            'confidence': round(confidence, 1),
            'consensus_count': max(buy_count, sell_count),
            'total_bots': len(self.bots),
            'signals': signals,
            'exit': exit_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }