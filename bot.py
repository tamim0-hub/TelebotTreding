import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, CHAT_ID, SYMBOLS, CHECK_INTERVAL_MINUTES
from orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_consensus(context: ContextTypes.DEFAULT_TYPE):
    """প্রতি ১৫ মিনিটে সব কয়েনের জন্য কনসেনসাস চেক করে"""
    chat_id = context.job.chat_id
    messages = []
    
    for symbol in SYMBOLS:
        orch = Orchestrator(symbol)
        result = orch.get_consensus()
        
        if result:
            # সিগন্যাল ফরম্যাট করা
            msg = f"✅ **SURE SHOT সিগন্যাল!** ({result['consensus_count']}/{result['total_bots']})\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"📈 কয়েন: {result['symbol']}\n"
            msg += f"🎯 অ্যাকশন: {result['action']} (কনফিডেন্স: {result['confidence']}%)\n\n"
            
            # প্রতিটি বটের সিগন্যাল
            for name, signal in result['signals'].items():
                emoji = '🟢' if signal['action'] == 'BUY' else '🔴' if signal['action'] == 'SELL' else '⚪'
                msg += f"{emoji} {name}: {signal['action']} ({signal['reason']})\n"
            
            # এক্সিট তথ্য
            if result['exit']:
                msg += f"\n🎯 টেক প্রফিট: ${result['exit']['tp']}\n"
                msg += f"🛑 স্টপ-লস: ${result['exit']['sl']}\n"
                msg += f"📈 রিস্ক:রিওয়ার্ড = ১:{result['exit']['risk_reward']}\n"
            
            msg += f"━━━━━━━━━━━━━━━━━━━━"
            messages.append(msg)
    
    # সব মেসেজ একসাথে পাঠানো
    if messages:
        for msg in messages[:5]:  # একবারে ৫টির বেশি না
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
            await asyncio.sleep(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await update.message.reply_text("⛔ এই বটটি ব্যক্তিগত ব্যবহারের জন্য।")
        return
    
    await update.message.reply_text(
        f"🤖 **মাল্টি-বট কনসেনসাস ইঞ্জিন চালু!**\n\n"
        f"📊 ট্র্যাক করা কয়েন: {', '.join(SYMBOLS)}\n"
        f"🧠 মোট বট: ৬টি (ট্রেন্ড, ওসিলেটর, ভলিউম, MACD, বলিঙ্গার, ইচিমোকু)\n"
        f"🎯 কনসেনসাস থ্রেশহোল্ড: {CONSENSUS_THRESHOLD}/{len(SYMBOLS)}\n"
        f"⏱️ প্রতি {CHECK_INTERVAL_MINUTES} মিনিটে চেক করা হবে।\n\n"
        f"_শুধুমাত্র কনসেনসাস তৈরি হলে সিগন্যাল পাঠানো হবে।_",
        parse_mode='Markdown'
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(
            send_consensus,
            interval=CHECK_INTERVAL_MINUTES * 60,
            first=10,
            chat_id=CHAT_ID
        )
        logger.info(f"✅ শিডিউল সেট: প্রতি {CHECK_INTERVAL_MINUTES} মিনিটে")
    
    logger.info("🤖 বট চালু হচ্ছে...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()