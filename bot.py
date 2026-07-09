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
    await send_signal_report(chat_id, context)

async def send_signal_report(chat_id, context):
    """সিগন্যাল রিপোর্ট তৈরি ও পাঠায়"""
    messages = []
    
    for symbol in SYMBOLS:
        orch = Orchestrator(symbol)
        result = orch.get_consensus()
        
        if result:
            # সিগন্যালের শক্তি নির্ধারণ
            if result['confidence'] >= 70:
                strength = "🔥 স্ট্রং"
            elif result['confidence'] >= 50:
                strength = "📊 মিডিয়াম"
            else:
                strength = "💨 উইক"
            
            if result['action'] == 'NEUTRAL' and result['confidence'] < 50:
                continue  # খুব দুর্বল সিগন্যাল স্কিপ করি
            
            msg = f"✅ **সিগন্যাল!** ({strength})\n"
            msg += f"━━━━━━━━━━━━━━━━━━━━\n"
            msg += f"📈 কয়েন: {result['symbol']}\n"
            msg += f"🎯 অ্যাকশন: {result['action']} (কনফিডেন্স: {result['confidence']}%)\n"
            msg += f"📊 স্কোর: BUY {result['score']['buy']} | SELL {result['score']['sell']}\n"
            msg += f"📊 কনসেনসাস: {result['consensus_count']}/{result['total_bots']}\n\n"
            
            # প্রতিটি বটের সিগন্যাল (সব না দেখিয়ে ৩টি দেখাই)
            count = 0
            for name, signal in result['signals'].items():
                if count >= 3:
                    break
                if signal['action'] != 'NEUTRAL':
                    emoji = '🟢' if signal['action'] == 'BUY' else '🔴' if signal['action'] == 'SELL' else '⚪'
                    msg += f"{emoji} {name}: {signal['action']} ({signal['reason']})\n"
                    count += 1
            
            if count == 0:
                msg += f"⚪ সব বট নিউট্রাল (কোনো স্পষ্ট সিগন্যাল নেই)\n"
            
            # এক্সিট তথ্য
            if result['exit']:
                msg += f"\n🎯 টেক প্রফিট: ${result['exit']['tp']}\n"
                msg += f"🛑 স্টপ-লস: ${result['exit']['sl']}\n"
                msg += f"📈 রিস্ক:রিওয়ার্ড = ১:{result['exit']['risk_reward']}\n"
            
            msg += f"━━━━━━━━━━━━━━━━━━━━"
            messages.append(msg)
    
    if messages:
        for msg in messages[:5]:  # একবারে ৫টির বেশি না
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
            await asyncio.sleep(1)
    else:
        # কোনো সিগন্যাল না পেলে জানিয়ে দেয়
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"⏳ {datetime.now().strftime('%I:%M %p')}: কোনো শক্তিশালী সিগন্যাল পাওয়া যায়নি। ১৫ মিনিট পর আবার চেক হবে।",
            parse_mode='Markdown'
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != CHAT_ID:
        await update.message.reply_text("⛔ এই বটটি ব্যক্তিগত ব্যবহারের জন্য।")
        return
    
    await update.message.reply_text(
        f"🤖 **মাল্টি-বট কনসেনসাস ইঞ্জিন চালু!**\n\n"
        f"📊 ট্র্যাক করা কয়েন: {', '.join(SYMBOLS)}\n"
        f"🧠 মোট বট: ৬টি (ট্রেন্ড, ওসিলেটর, ভলিউম, MACD, বলিঙ্গার, ইচিমোকু)\n"
        f"🎯 সিগন্যাল থ্রেশহোল্ড: {SIGNAL_THRESHOLD}%\n"
        f"⏱️ অটো চেক: প্রতি {CHECK_INTERVAL_MINUTES} মিনিটে\n\n"
        f"📌 **কমান্ডসমূহ:**\n"
        f"🔹 /start - বট চালু করুন\n"
        f"🔹 /signal - এখনই সিগন্যাল চেক করুন\n"
        f"🔹 /status - বটের অবস্থা জানুন\n\n"
        f"_শুধুমাত্র ভালো সিগন্যাল এলে মেসেজ পাঠানো হবে। দুর্বল সিগন্যাল স্কিপ করা হয়।_",
        parse_mode='Markdown'
    )

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'/signal' কমান্ড - সঙ্গে সঙ্গে সিগন্যাল চেক করে"""
    if str(update.effective_chat.id) != CHAT_ID:
        await update.message.reply_text("⛔ এই বটটি ব্যক্তিগত ব্যবহারের জন্য।")
        return
    
    await update.message.reply_text("⏳ সিগন্যাল চেক করা হচ্ছে, একটু অপেক্ষা করুন...")
    await send_signal_report(CHAT_ID, context)

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'/status' কমান্ড - বটের অবস্থা জানায়"""
    if str(update.effective_chat.id) != CHAT_ID:
        return
    
    await update.message.reply_text(
        f"🟢 **বট সচল আছে!**\n\n"
        f"📊 ট্র্যাক করা কয়েন: {len(SYMBOLS)}টি\n"
        f"🧠 বট: ৬টি অ্যালগরিদম\n"
        f"⏱️ চেক ইন্টারভাল: {CHECK_INTERVAL_MINUTES} মিনিট\n"
        f"🕐 বর্তমান সময়: {datetime.now().strftime('%I:%M %S %p')}\n\n"
        f"_বট ঠিকমতো কাজ করছে। /signal দিয়ে সিগন্যাল চেক করুন।_",
        parse_mode='Markdown'
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # কমান্ড হ্যান্ডলার
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    
    # অটো শিডিউল
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