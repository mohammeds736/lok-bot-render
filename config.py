import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# الإعدادات الأساسية
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PLATFORM = os.environ.get('PLATFORM', 'web').lower()

# إعدادات التلقائي
AUTO_CONFIG = {
    'resource_interval': int(os.environ.get('RESOURCE_INTERVAL', '30')),
    'attack_interval': int(os.environ.get('ATTACK_INTERVAL', '45')),
    'training_interval': int(os.environ.get('TRAINING_INTERVAL', '60')),
}

# التحقق من الإعدادات
def validate_config():
    errors = []
    
    if not BOT_TOKEN:
        errors.append("❌ BOT_TOKEN مطلوب")
    
    if PLATFORM not in ['android', 'ios', 'web']:
        errors.append("❌ PLATFORM يجب أن يكون: android, ios, or web")
    
    return errors

# التحقق عند الاستيراد
config_errors = validate_config()
if config_errors:
    for error in config_errors:
        print(error)
