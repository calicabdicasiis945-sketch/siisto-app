from django import template
from django.utils import translation

register = template.Library()

UI_TRANSLATIONS = {
    # Navigation & General
    "Dashboard": {"so": "Kala-bixidda Guud (Dashboard)", "en": "Dashboard", "ar": "لوحة التحكم (Dashboard)"},
    "AI Coach": {"so": "Macallinka AI (AI Coach)", "en": "AI Coach", "ar": "مدرب الذكاء الاصطناعي"},
    "AI Form Detection": {"so": "Falanqaynta Qaabka AI", "en": "AI Form Detection", "ar": "تحليل الوضعية بالذكاء الاصطناعي"},
    "90-Day Challenge": {"so": "Tartanka 90-ka Maalmood", "en": "90-Day Challenge", "ar": "تحدي الـ 90 يوماً"},
    "AI Plan Generator": {"so": "Sameeyaha Qorshaha AI", "en": "AI Plan Generator", "ar": "منشئ الخطط الذكي"},
    "3D Exercises Library": {"so": "Maktabadda Jimicsiyada 3D", "en": "3D Exercises Library", "ar": "مكتبة التمارين ثلاثية الأبعاد"},
    "Cuntooyinka (Meals)": {"so": "Cuntooyinka", "en": "Meals & Nutrition", "ar": "الوجبات والتغذية"},
    "Meals": {"so": "Cuntooyinka", "en": "Meals", "ar": "الوجبات"},
    "3D Body Scan": {"so": "Sawirka Jirka 3D", "en": "3D Body Scan", "ar": "المسح ثلاثي الأبعاد للجسم"},
    "Analytics / Hormarka": {"so": "Falanqaynta & Hormarka", "en": "Analytics & Progress", "ar": "التحليلات والتقدم"},
    "Analytics": {"so": "Falanqaynta", "en": "Analytics", "ar": "التحليلات"},
    "Diiwaanka / History": {"so": "Taariikhda & Diiwaanka", "en": "History & Logs", "ar": "السجل والتاريخ"},
    "History": {"so": "Taariikhda", "en": "History", "ar": "السجل"},
    "Admin Control": {"so": "Maamulka Xafiiska", "en": "Admin Control", "ar": "لوحة الإدارة"},
    "Upgrade To Pro": {"so": "U Gudub Pro", "en": "Upgrade to Pro", "ar": "الترقية إلى برو"},
    "Settings & Profile": {"so": "Dejinta & Profile-ka", "en": "Settings & Profile", "ar": "الإعدادات والملف الشخصي"},
    "Settings": {"so": "Dejinta", "en": "Settings", "ar": "الإعدادات"},
    "Profile": {"so": "Profile-ka", "en": "Profile", "ar": "الملف الشخصي"},
    "Log out": {"so": "Ka Bax", "en": "Log Out", "ar": "تسجيل الخروج"},
    "Login": {"so": "Gal", "en": "Log In", "ar": "تسجيل الدخول"},
    "Sign Up": {"so": "Is-diiwaangeli", "en": "Sign Up", "ar": "إنشاء حساب"},
    "Signup": {"so": "Is-diiwaangeli", "en": "Sign Up", "ar": "إنشاء حساب"},
    "Welcome back": {"so": "Ku soo dhowow mar kale", "en": "Welcome back", "ar": "مرحباً بعودتك"},
    "Daily Calories": {"so": "Tamar-cuntada Maanta", "en": "Daily Calories", "ar": "السعرات اليومية"},
    "Daily Protein": {"so": "Borotiinka Maanta", "en": "Daily Protein", "ar": "البروتين اليومي"},
    "Workouts Logged": {"so": "Jimicsiyada La Qabtay", "en": "Workouts Logged", "ar": "التمارين المسجلة"},
    "Workout Streak": {"so": "Joogteynta Jimicsiga", "en": "Workout Streak", "ar": "سلسلة الالتزام بالتمارين"},
    "Recent Activity": {"so": "Dhaqdhaqaaqyadii Ugu Dambeeyay", "en": "Recent Activity", "ar": "النشاط الأخير"},
    "Track Your Progress": {"so": "La Soco Hormarkaaga", "en": "Track Your Progress", "ar": "تتبع تقدمك الرياضي"},
    "Save": {"so": "Keydi", "en": "Save", "ar": "حفظ"},
    "Cancel": {"so": "Ka Noqo", "en": "Cancel", "ar": "إلغاء"},
    "Edit": {"so": "Wax Ka Beddel", "en": "Edit", "ar": "تعديل"},
    "Delete": {"so": "Tirtir", "en": "Delete", "ar": "حذف"},
    "Weight": {"so": "Miisaanka", "en": "Weight", "ar": "الوزن"},
    "Height": {"so": "Dhererka", "en": "Height", "ar": "الطول"},
    "Target Weight": {"so": "Yoolka Miisaanka", "en": "Target Weight", "ar": "الوزن المستهدف"},
    "Fitness Goal": {"so": "Hadafka Jimicsiga", "en": "Fitness Goal", "ar": "الهدف الرياضي"},
    "Activity Level": {"so": "Heerka Dhaqdhaqaaqa", "en": "Activity Level", "ar": "مستوى النشاط"},
    "Fitness Level": {"so": "Heerka Tababarka", "en": "Fitness Level", "ar": "مستوى اللياقة"},
    "Experience Level": {"so": "Heerka Khibradda", "en": "Experience Level", "ar": "مستوى الخبرة"},
    "Age": {"so": "Da'da", "en": "Age", "ar": "العمر"},
    "Gender": {"so": "Jinsiga", "en": "Gender", "ar": "الجنس"},
    
    # Categories
    "Chest": {"so": "Xabadka", "en": "Chest", "ar": "الصدر"},
    "Back": {"so": "Dhabarka", "en": "Back", "ar": "الظهر"},
    "Shoulders": {"so": "Garabka", "en": "Shoulders", "ar": "الأكتاف"},
    "Arms": {"so": "Gacmaha", "en": "Arms", "ar": "الذراعين"},
    "Legs": {"so": "Lugaha", "en": "Legs", "ar": "الأرجل"},
    "Abs / Core": {"so": "Caloosha & Bartamaha", "en": "Abs & Core", "ar": "البطن والوسط"},
    "Cardio": {"so": "Wadnaha & Orodka", "en": "Cardio", "ar": "كارديو"},
    
    # Exercises
    "Squats": {"so": "Istaag & Fariiso (Squats)", "en": "Squats", "ar": "سكوات (القرفصاء)"},
    "Push-Ups": {"so": "Riixid (Push-Ups)", "en": "Push-Ups", "ar": "تمرين الضغط (Push-Ups)"},
    "Bicep Curls": {"so": "Curashada Gacanta (Bicep Curls)", "en": "Bicep Curls", "ar": "بايسبس كيرل (Bicep Curls)"},
    "Shoulder Press": {"so": "Riixidda Garabka (Shoulder Press)", "en": "Shoulder Press", "ar": "ضغط الأكتاف (Shoulder Press)"},
    "Lunges": {"so": "Talaabada Lugaha (Lunges)", "en": "Lunges", "ar": "طعنات الأرجل (Lunges)"},
    "Plank": {"so": "Toosinta Jirka (Plank)", "en": "Plank", "ar": "بلانك (Plank)"},
    "Sit-Ups": {"so": "Kac & Fariiso (Sit-Ups)", "en": "Sit-Ups", "ar": "تمارين البطن (Sit-Ups)"},
    "Lateral Raises": {"so": "Taagidda Garabka (Lateral Raises)", "en": "Lateral Raises", "ar": "الرفرفة الجانبية (Lateral Raises)"},
    "Deadlifts": {"so": "Kicinta Miisaanka (Deadlifts)", "en": "Deadlifts", "ar": "ديدليفت (Deadlifts)"},

    # Actions & Form
    "Language": {"so": "Luqadda", "en": "Language", "ar": "اللغة"},
    "Start Camera": {"so": "Daar Kamarada", "en": "Start Camera", "ar": "تشغيل الكاميرا"},
    "Stop Camera": {"so": "Jooji Kamarada", "en": "Stop Camera", "ar": "إيقاف الكاميرا"},
    "Good form!": {"so": "Farsamo sax ah!", "en": "Good form!", "ar": "وضعية ممتازة!"},
    "Adjust form": {"so": "Saxo farsamada", "en": "Adjust form", "ar": "تعديل الوضعية"},
    "Completed Reps": {"so": "Tirada La Sameeyay", "en": "Completed Reps", "ar": "التكرارات المنجزة"},
    "Days Completed": {"so": "Maalmaha La Dhamaystiray", "en": "Days Completed", "ar": "الأيام المنجزة"},
    "Current Streak": {"so": "Joogteynta Hadda", "en": "Current Streak", "ar": "السلسلة الحالية"},
    "Upgrade": {"so": "U Gudub Pro", "en": "Upgrade", "ar": "ترقية"},
    "Pro Active": {"so": "Xubinnimada Pro Way Shaqaynaysaa", "en": "Pro Active", "ar": "عضوية برو نشطة"},
    "Free Tier": {"so": "Heerka Bilaashka ah", "en": "Free Tier", "ar": "المستوى المجاني"},
    "Voice Feedback": {"so": "Codka Caawiyaha", "en": "Voice Feedback", "ar": "التوجيه الصوتي"},
    "Reset Reps": {"so": "Dib u billow Tirada", "en": "Reset Reps", "ar": "إعادة ضبط العداد"},
    "Calories": {"so": "Kalooriyada", "en": "Calories", "ar": "السعرات الحرارية"},
    "Protein": {"so": "Borotiinka", "en": "Protein", "ar": "البروتين"},
    "Carbs": {"so": "Karbohaydraytka", "en": "Carbs", "ar": "الكربوهيدرات"},
    "Fats": {"so": "Dufanka", "en": "Fats", "ar": "الدهون"},
    "Nutrition": {"so": "Nafaqada", "en": "Nutrition", "ar": "التغذية"},
    "Workout": {"so": "Jimicsiga", "en": "Workout", "ar": "التمرين"},
    "Exercises": {"so": "Jimicsiyada", "en": "Exercises", "ar": "التمارين"},
    "Add Meal": {"so": "Ku Dar Cunto", "en": "Add Meal", "ar": "إضافة وجبة"},
    "Add Workout": {"so": "Ku Dar Jimicsi", "en": "Add Workout", "ar": "إضافة تمرين"},
    "Log Weight": {"so": "Diiwaangeli Miisaan", "en": "Log Weight", "ar": "تسجيل الوزن"},
    "Main Menu": {"so": "Liiska Guud", "en": "Main Menu", "ar": "القائمة الرئيسية"},
    "Account": {"so": "Koontada", "en": "Account", "ar": "الحساب"},
}

@register.filter(name='ui_trans')
def ui_trans(key, lang=None):
    if not key:
        return ""
    if not lang:
        lang = translation.get_language() or 'so'
    lang_prefix = lang[:2].lower()
    if key in UI_TRANSLATIONS:
        return UI_TRANSLATIONS[key].get(lang_prefix, UI_TRANSLATIONS[key].get('en', key))
    return key
