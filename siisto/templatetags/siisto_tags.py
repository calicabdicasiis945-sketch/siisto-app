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
    "3D Body Scan": {"so": "Sawirka Jirka 3D & Qiimeynta", "en": "3D Body Scan & Assessment", "ar": "المسح ثلاثي الأبعاد للجسم والتقييم"},
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

    # 3D Body Scan & Assessment Questions
    "3D Body Scan Title": {
        "so": "Sawirka Jirka 3D & Qiimeynta Biometrics",
        "en": "3D Body Scan & Biometric Assessment",
        "ar": "المسح ثلاثي الأبعاد للجسم والتقييم الحيوي"
    },
    "3D Body Scan Subtitle": {
        "so": "360° Qiimee Jirkaaga, Xisaabi BMI, BMR, TDEE, iyo Kalooriyadaada",
        "en": "360° Biometric Body Assessment, BMI, BMR, TDEE & Target Calories",
        "ar": "تقييم ثلاثي الأبعاد 360°، حساب مؤشر الكتلة BMI، BMR، السعرات والماكروز"
    },
    "Start 3D Scan": {
        "so": "Bilaaw 3D Body Scan",
        "en": "Start 3D Body Scan",
        "ar": "بدء المسح ثلاثي الأبعاد"
    },
    "Step 1: Gender": {
        "so": "Talaabada 1: Dooro Jinsiga",
        "en": "Step 1: Select Gender",
        "ar": "الخطوة 1: اختر الجنس"
    },
    "Male": {
        "so": "Lab (Male)",
        "en": "Male",
        "ar": "ذكر (Male)"
    },
    "Female": {
        "so": "Dhedig (Female)",
        "en": "Female",
        "ar": "أنثى (Female)"
    },
    "Step 2: Biometrics": {
        "so": "Talaabada 2: Da'da, Dhererka & Miisaanka",
        "en": "Step 2: Age, Height & Current Weight",
        "ar": "الخطوة 2: العمر، الطول والوزن الحالي"
    },
    "Step 3: Goal": {
        "so": "Talaabada 3: Waa Maxay Hadafkaagu?",
        "en": "Step 3: What is Your Primary Fitness Goal?",
        "ar": "الخطوة 3: ما هو هدفك الرياضي الأساسي؟"
    },
    "Lose Weight": {
        "so": "Miisaan Dhimis (Fat Loss)",
        "en": "Lose Weight / Fat Loss",
        "ar": "حرق الدهون وإنقاص الوزن"
    },
    "Build Muscle": {
        "so": "Muruq Dhis (Muscle Gain)",
        "en": "Build Muscle / Hypertrophy",
        "ar": "بناء العضلات والتضخيم"
    },
    "Maintain Fitness": {
        "so": "Joogteyn & Awood (Maintain)",
        "en": "Maintain & Fitness",
        "ar": "المحافظة على اللياقة والصحة"
    },
    "Step 4: Activity": {
        "so": "Talaabada 4: Heerka Dhaqdhaqaaqaaga Maalinlaha ah",
        "en": "Step 4: Daily Physical Activity Level",
        "ar": "الخطوة 4: مستوى نشاطك البدني اليومي"
    },
    "Sedentary": {
        "so": "Fadhiga Badan (Office / Little Exercise)",
        "en": "Sedentary (Little to no exercise)",
        "ar": "خامل (قليل الحركة / عمل مكتبي)"
    },
    "Moderate": {
        "so": "Dhexdhexaad (3-4 maalmood tababar)",
        "en": "Moderate (3-4 workouts/week)",
        "ar": "متوسط (3-4 أيام تمرين أسبوعياً)"
    },
    "Active": {
        "so": "Firfircoon (5-6 maalmood tababar adag)",
        "en": "Active (5-6 intense workouts/week)",
        "ar": "نشط جداً (5-6 أيام تمرين قوي)"
    },
    "Step 5: Target Weight": {
        "so": "Talaabada 5: Yoolka Miisaanka Aad Rabto (Target Weight)",
        "en": "Step 5: Your Target Goal Weight",
        "ar": "الخطوة 5: الوزن المستهدف تحقيقه"
    },
    "Calculate & Scan": {
        "so": "Xisaabi & Soo Saari Natiijada 3D",
        "en": "Calculate & Generate 3D Scan",
        "ar": "احسب واستخرج تقرير المسح ثلاثي الأبعاد"
    },
    "Save Assessment": {
        "so": "Keydi Xogta Profile-ka",
        "en": "Save to Profile",
        "ar": "حفظ البيانات في الملف الشخصي"
    },
    "Scan Complete": {
        "so": "Qiimeynta 3D Waa La Dhamaystiray!",
        "en": "3D Assessment Complete!",
        "ar": "تم اكتمال المسح والتقييم ثلاثي الأبعاد بنجاح!"
    },
    
    # Biometric Metrics
    "Body Mass Index": {"so": "Tusmada Miisaanka (BMI)", "en": "Body Mass Index (BMI)", "ar": "مؤشر كتلة الجسم (BMI)"},
    "Basal Metabolic Rate": {"so": "Tamar-gubidda Asaasiga ah (BMR)", "en": "Basal Metabolic Rate (BMR)", "ar": "معدل الأيض الأساسي (BMR)"},
    "Total Daily Energy": {"so": "Wadarta Tamarta Maalintii (TDEE)", "en": "Total Daily Energy (TDEE)", "ar": "إجمالي استهلاك الطاقة اليومي (TDEE)"},
    "Target Daily Calories": {"so": "Kalooriyada Yoolka Maanta", "en": "Target Daily Calories", "ar": "السعرات اليومية المستهدفة"},
    "Daily Protein Target": {"so": "Yoolka Borotiinka Maalintii", "en": "Daily Protein Target", "ar": "احتياج البروتين اليومي"},
    "Daily Water Target": {"so": "Biyaha La Cabbo Maalintii", "en": "Daily Water Target", "ar": "كمية الماء اليومية الموصى بها"},
    "Estimated Time": {"so": "Waqtiga La Qiyaasay", "en": "Estimated Timeframe", "ar": "المدة الزمنية التقديرية"},

    # 360 Rotation Controls
    "360 Rotation": {"so": "Wareegga 360°", "en": "360° Rotation", "ar": "دوران 360 درجة"},
    "Front View": {"so": "Qaybta Hore", "en": "Front View", "ar": "الجهة الأمامية"},
    "Side View": {"so": "Dhinaca", "en": "Side View", "ar": "الجهة الجانبية"},
    "Back View": {"so": "Dhabarka", "en": "Back View", "ar": "الجهة الخلفية"},

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

    # Mobile Nav Bar
    "Home": {"so": "Guriga", "en": "Home", "ar": "الرئيسية"},
    "Workouts": {"so": "Jimicsiyada", "en": "Workouts", "ar": "التمارين"},
    "Progress": {"so": "Hormarka", "en": "Progress", "ar": "التقدم"},

    # Extra UI labels
    "Loading": {"so": "Waa la Rarayo...", "en": "Loading...", "ar": "جارٍ التحميل..."},
    "View All": {"so": "Arag Dhammaan", "en": "View All", "ar": "عرض الكل"},
    "No data yet": {"so": "Xog ma jirto wali", "en": "No data yet", "ar": "لا توجد بيانات بعد"},
    "Today": {"so": "Maanta", "en": "Today", "ar": "اليوم"},
    "Week": {"so": "Usbuuca", "en": "Week", "ar": "الأسبوع"},
    "Month": {"so": "Bishaa", "en": "Month", "ar": "الشهر"},
    "Submit": {"so": "Dir", "en": "Submit", "ar": "إرسال"},
    "Next": {"so": "Xiga", "en": "Next", "ar": "التالي"},
    "Back": {"so": "Dib", "en": "Back", "ar": "رجوع"},
    "Finish": {"so": "Dhammee", "en": "Finish", "ar": "إنهاء"},
    "Complete": {"so": "Dhammeystir", "en": "Complete", "ar": "اكتمل"},
    "Start": {"so": "Bilaaw", "en": "Start", "ar": "ابدأ"},
    "View Details": {"so": "Arag Faahfaahinta", "en": "View Details", "ar": "عرض التفاصيل"},
    "Add Exercise": {"so": "Ku Dar Jimicsi", "en": "Add Exercise", "ar": "إضافة تمرين"},
    "Search": {"so": "Raadi", "en": "Search", "ar": "بحث"},
    "Filter": {"so": "Shaandee", "en": "Filter", "ar": "تصفية"},
    "Send": {"so": "Dir", "en": "Send", "ar": "إرسال"},
    "Type a message": {"so": "Qor fariin...", "en": "Type a message...", "ar": "اكتب رسالة..."},

    # AI Coach Chatbot
    "ai_welcome_pro": {"so": "Ku soo dhowow Siisto AI Elite Master Coach (VIP)! 👑", "en": "Welcome to Siisto AI Elite Master Coach (VIP)! 👑", "ar": "مرحباً بك في مدرب Siisto AI النخبة (VIP)! 👑"},
    "ai_welcome_free": {"so": "Ku soo dhowow Siisto AI Assistant! 👋", "en": "Welcome to Siisto AI Assistant! 👋", "ar": "مرحباً بك في Siisto AI Assistant! 👋"},
    "ai_welcome_body": {"so": "Waxaan ahay tababarahaaga gaarka ah. Waxaad i weydiin kartaa su'aal kasta oo ku saabsan:", "en": "I am your personal coach. You can ask me anything about:", "ar": "أنا مدربك الشخصي. يمكنك أن تسألني عن:"},
    "ai_topic_1": {"so": "Miisaan kordhin (Weight Gain) & Dhimis (Fat Loss).", "en": "Weight Gain & Fat Loss strategies.", "ar": "استراتيجيات زيادة الوزن وحرق الدهون."},
    "ai_topic_2": {"so": "Cuntooyinka borotiinka leh & xisaabinta Calories-ka.", "en": "High-protein meals & Calorie calculations.", "ar": "الوجبات الغنية بالبروتين وحساب السعرات."},
    "ai_topic_3": {"so": "Jadwalka jimicsiga Gym-ka & qaabka saxda ah.", "en": "Gym workout schedules & proper form.", "ar": "جداول تمارين الجيم والأوضاع الصحيحة."},
    "ai_cta": {"so": "I weydii su'aashaada hadda si aynu u bilowno!", "en": "Ask me your question now and let's begin!", "ar": "اسألني الآن ولنبدأ معاً!"},
    "AI is thinking": {"so": "Siisto AI ayaa fekeraysa...", "en": "Siisto AI is thinking...", "ar": "Siisto AI يفكّر..."},
    "ai_thinking": {"so": "Siisto AI ayaa fekeraysa...", "en": "Siisto AI is thinking...", "ar": "Siisto AI يفكّر..."},
    "chat_placeholder": {"so": "Halkan ku qor su'aashaada (Tusaale: Sideen muruq u dhisaa?)...", "en": "Ask your fitness question here (e.g. How do I build muscle?)...", "ar": "اكتب سؤالك هنا (مثال: كيف أبني العضلات؟)..."},

    # Chatbot limit / meta
    "ai_remaining": {"so": "fariin oo bilaash ah maanta", "en": "free messages today", "ar": "رسائل مجانية اليوم"},
    "limit_reached_title": {"so": "Xadka Maanta Ayaad Gaadhtay!", "en": "Daily Limit Reached!", "ar": "وصلت إلى الحد اليومي!"},
    "limit_reached_body": {"so": "Qorshe bilaashku wuxuu kuu oggol yahay", "en": "Free plan allows", "ar": "الخطة المجانية تسمح بـ"},
    "messages": {"so": "fariin", "en": "messages", "ar": "رسالة"},
    "clear_chat": {"so": "Nadiifi Shaashadda", "en": "Clear Chat", "ar": "مسح المحادثة"},
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
