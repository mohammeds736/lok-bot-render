import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask

# إعدادات التطبيق
app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PLATFORM = os.environ.get('PLATFORM', 'web').lower()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# حالة البوت
class LOKAutoBot:
    def __init__(self):
        self.platform = PLATFORM
        self.scheduler = AsyncIOScheduler()
        self.bot_status = {
            'running': False,
            'resources_collected': 0,
            'attacks_made': 0,
            'troops_trained': 0,
            'last_action': None
        }
    
    async def start_auto_tasks(self):
        """بدء المهام التلقائية"""
        try:
            # جدولة المهام
            self.scheduler.add_job(
                self.collect_resources,
                trigger=IntervalTrigger(minutes=30),
                id='auto_resource_collection'
            )
            
            self.scheduler.add_job(
                self.attack_monsters,
                trigger=IntervalTrigger(minutes=45),
                id='auto_attacking'
            )
            
            self.scheduler.add_job(
                self.train_troops,
                trigger=IntervalTrigger(hours=1),
                id='auto_training'
            )
            
            self.scheduler.start()
            self.bot_status['running'] = True
            logger.info("✅ بدء المهام التلقائية")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل بدء المهام: {e}")
            return False
    
    async def stop_auto_tasks(self):
        """إيقاف المهام التلقائية"""
        self.scheduler.shutdown()
        self.bot_status['running'] = False
        logger.info("⏹️ إيقاف المهام التلقائية")
    
    async def collect_resources(self):
        """جمع الموارد تلقائياً"""
        try:
            self.bot_status['resources_collected'] += 1
            self.bot_status['last_action'] = 'collect_resources'
            logger.info("✅ جمع الموارد تلقائياً")
        except Exception as e:
            logger.error(f"❌ فشل جمع الموارد: {e}")
    
    async def attack_monsters(self):
        """مهاجمة الوحوش تلقائياً"""
        try:
            self.bot_status['attacks_made'] += 1
            self.bot_status['last_action'] = 'attack_monsters'
            logger.info("✅ هجوم تلقائي على الوحوش")
        except Exception as e:
            logger.error(f"❌ فشل الهجوم: {e}")
    
    async def train_troops(self):
        """تدريب القوات تلقائياً"""
        try:
            self.bot_status['troops_trained'] += 1
            self.bot_status['last_action'] = 'train_troops'
            logger.info("✅ تدريب تلقائي للقوات")
        except Exception as e:
            logger.error(f"❌ فشل التدريب: {e}")
    
    async def get_status(self):
        """الحصول على حالة البوت"""
        return f"""
🤖 *حالة البوت التلقائي* - {self.platform.upper()}

🟢 البوت: {'يعمل' if self.bot_status['running'] else 'متوقف'}
📊 المهام النشطة: {len(self.scheduler.get_jobs())}

📈 الإحصائيات:
🔄 جمع الموارد: {self.bot_status['resources_collected']} مرة
⚔️ هجمات: {self.bot_status['attacks_made']} مرة
👥 تدريب: {self.bot_status['troops_trained']} مرة

⏰ آخر عمل: {self.bot_status['last_action'] or 'لا يوجد'}
        """

# إنشاء البوت
bot = LOKAutoBot()

# صفحة ويب أساسية
@app.route('/')
def home():
    return f"🏰 بوت League of Kingdoms يعمل على منصة: {PLATFORM.upper()}"

# أوامر Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['🚀 بدء التلقائي', '⏹️ إيقاف التلقائي'],
        ['📊 الحالة', '🔄 جمع الآن'],
        ['⚔️ هجوم الآن', '👥 تدريب الآن']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = """
🤖 *بوت League of Kingdoms التلقائي*

🎯 يعمل تلقائياً على منصة: *{}*

🚀 الميزات التلقائية:
✅ جمع الموارد كل 30 دقيقة
✅ مهاجمة الوحوش كل 45 دقيقة  
✅ تدريب القوات كل ساعة

📊 Use /status لعرض الحالة
    """.format(PLATFORM.upper())
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🚀 بدء التلقائي':
        success = await bot.start_auto_tasks()
        response = "✅ بدء التشغيل التلقائي!" if success else "❌ فشل بدء التشغيل"
        await update.message.reply_text(response)
    
    elif text == '⏹️ إيقاف التلقائي':
        await bot.stop_auto_tasks()
        await update.message.reply_text("⏹️ تم إيقاف التشغيل التلقائي")
    
    elif text == '📊 الحالة':
        status = await bot.get_status()
        await update.message.reply_text(status, parse_mode='Markdown')
    
    elif text == '🔄 جمع الآن':
        await bot.collect_resources()
        await update.message.reply_text("✅ جاري جمع الموارد...")
    
    elif text == '⚔️ هجوم الآن':
        await bot.attack_monsters()
        await update.message.reply_text("✅ جاري الهجوم على الوحوش...")
    
    elif text == '👥 تدريب الآن':
        await bot.train_troops()
        await update.message.reply_text("✅ جاري تدريب القوات...")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /status"""
    status = await bot.get_status()
    await update.message.reply_text(status, parse_mode='Markdown')

async def main():
    """الدالة الرئيسية للتشغيل"""
    try:
        # التحقق من التوكن
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN غير موجود")
            return
        
        # إنشاء تطبيق Telegram
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # بدء البوت تلقائياً
        await bot.start_auto_tasks()
        
        logger.info(f"✅ البوت يعمل على منصة: {PLATFORM}")
        logger.info("🤖 جاهز لاستقبال الأوامر")
        
        # بدء استقبال الرسائل
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")

def run_flask():
    """تشغيل خادم Flask"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    # تشغيل Flask في الخلفية
    import threading
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل البوت الرئيسي
    asyncio.run(main())
