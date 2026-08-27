import os
import struct
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def generate_mo(translations, output_path):
    """
    Pure Python generator for binary GNU gettext .mo files.
    translations: dict of {msgid: msgstr}
    """
    keys = sorted(translations.keys())
    # Msgid 0 is header
    header = "Project-Id-Version: Siisto 1.0\nReport-Msgid-Bugs-To: \nPO-Revision-Date: 2026-08-26 12:00+0000\nLast-Translator: Siisto Team\nLanguage-Team: \nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n"
    all_keys = [''] + [k for k in keys if k != '']
    all_values = [header] + [translations[k] for k in all_keys if k != '']

    num_strings = len(all_keys)
    
    orig_table = []
    trans_table = []
    
    orig_data = bytearray()
    trans_data = bytearray()
    
    for k in all_keys:
        k_bytes = k.encode('utf-8')
        orig_table.append((len(k_bytes), len(orig_data)))
        orig_data.extend(k_bytes + b'\x00')
        
    for v in all_values:
        v_bytes = v.encode('utf-8')
        trans_table.append((len(v_bytes), len(trans_data)))
        trans_data.extend(v_bytes + b'\x00')
        
    keystart = 7 * 4
    valuestart = keystart + num_strings * 8
    keydata = valuestart + num_strings * 8
    valuedata = keydata + len(orig_data)
    
    output = bytearray()
    output.extend(struct.pack(
        "Iiiiiii",
        0x950412DE,  # Magic number
        0,           # Format revision
        num_strings, # Number of strings
        keystart,    # Offset of original string table
        valuestart,  # Offset of translation string table
        0,           # Size of hashing table
        0            # Offset of hashing table
    ))
    
    for length, offset in orig_table:
        output.extend(struct.pack("ii", length, keydata + offset))
        
    for length, offset in trans_table:
        output.extend(struct.pack("ii", length, valuedata + offset))
        
    output.extend(orig_data)
    output.extend(trans_data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(output)

def generate_po(translations, output_path, lang_name):
    lines = [
        'msgid ""',
        'msgstr ""',
        '"Project-Id-Version: Siisto 1.0\\n"',
        f'"Language: {lang_name}\\n"',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        '',
    ]
    for k, v in translations.items():
        if not k:
            continue
        clean_k = k.replace('"', '\\"').replace('\n', '\\n"\n"')
        clean_v = v.replace('"', '\\"').replace('\n', '\\n"\n"')
        lines.append(f'msgid "{clean_k}"')
        lines.append(f'msgstr "{clean_v}"')
        lines.append('')
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

TRANSLATIONS_SO = {
    "Dashboard": "Dashboard-ka",
    "AI Coach": "AI Coach",
    "AI Form Detection": "Falanqaynta Qaabka AI",
    "90-Day Challenge": "Tartanka 90-ka Maalmood",
    "AI Plan Generator": "Sameeyaha Qorshaha AI",
    "3D Exercises Library": "Maktabadda Jimicsiyada 3D",
    "Cuntooyinka (Meals)": "Cuntooyinka",
    "Meals": "Cuntooyinka",
    "3D Body Scan": "Sawirka Jirka 3D",
    "Analytics / Hormarka": "Falanqaynta & Hormarka",
    "Analytics": "Falanqaynta",
    "Diiwaanka / History": "Taariikhda & Diiwaanka",
    "History": "Taariikhda",
    "Admin Control": "Maamulka Xafiiska",
    "Upgrade To Pro": "U Gudub Pro",
    "Settings & Profile": "Dejinta & Profile-ka",
    "Settings": "Dejinta",
    "Profile": "Profile-ka",
    "Log out": "Ka Bax",
    "Login": "Gal",
    "Sign Up": "Is-diiwaangeli",
    "Signup": "Is-diiwaangeli",
    "Welcome back": "Ku soo dhowow mar kale",
    "Daily Calories": "Tamar-cuntada Maanta",
    "Daily Protein": "Borotiinka Maanta",
    "Workouts Logged": "Jimicsiyada La Qabtay",
    "Workout Streak": "Joogteynta Jimicsiga",
    "Recent Activity": "Dhaqdhaqaaqyadii Ugu Dambeeyay",
    "Track Your Progress": "La Soco Hormarkaaga",
    "Save": "Keydi",
    "Cancel": "Ka Noqo",
    "Edit": "Wax Ka Beddel",
    "Delete": "Tirtir",
    "Weight": "Miisaanka",
    "Height": "Dhererka",
    "Target Weight": "Yoolka Miisaanka",
    "Fitness Goal": "Hadafka Jimicsiga",
    "Activity Level": "Heerka Dhaqdhaqaaqa",
    "Fitness Level": "Heerka Tababarka",
    "Experience Level": "Heerka Khibradda",
    "Age": "Da'da",
    "Gender": "Jinsiga",
    "Chest": "Xabadka",
    "Back": "Dhabarka",
    "Shoulders": "Garabka",
    "Arms": "Gacmaha",
    "Legs": "Lugaha",
    "Abs / Core": "Caloosha & Bartamaha",
    "Cardio": "Wadnaha & Orodka",
    "Squats": "Istaag & Fariiso (Squats)",
    "Push-Ups": "Riixid (Push-Ups)",
    "Bicep Curls": "Curashada Gacanta (Bicep Curls)",
    "Shoulder Press": "Riixidda Garabka (Shoulder Press)",
    "Lunges": "Talaabada Lugaha (Lunges)",
    "Plank": "Toosinta Jirka (Plank)",
    "Sit-Ups": "Kac & Fariiso (Sit-Ups)",
    "Lateral Raises": "Taagidda Garabka (Lateral Raises)",
    "Deadlifts": "Kicinta Miisaanka (Deadlifts)",
    "Language": "Luqadda",
    "Start Camera": "Daar Kamarada",
    "Stop Camera": "Jooji Kamarada",
    "Good form!": "Farsamo sax ah!",
    "Adjust form": "Saxo farsamada",
    "Completed Reps": "Tirada La Sameeyay",
    "Days Completed": "Maalmaha La Dhamaystiray",
    "Current Streak": "Joogteynta Hadda",
    "Upgrade": "U Gudub Pro",
    "Pro Active": "Xubinnimada Pro Way Shaqaynaysaa",
    "Free Tier": "Heerka Bilaashka ah",
    "Voice Feedback": "Codka Caawiyaha",
    "Reset Reps": "Dib u billow Tirada",
    "Calories": "Kalooriyada",
    "Protein": "Borotiinka",
    "Carbs": "Karbohaydraytka",
    "Fats": "Dufanka",
    "Nutrition": "Nafaqada",
    "Workout": "Jimicsiga",
    "Exercises": "Jimicsiyada",
    "Add Meal": "Ku Dar Cunto",
    "Add Workout": "Ku Dar Jimicsi",
    "Log Weight": "Diiwaangeli Miisaan",
}

TRANSLATIONS_EN = {
    "Dashboard": "Dashboard",
    "AI Coach": "AI Coach",
    "AI Form Detection": "AI Form Detection",
    "90-Day Challenge": "90-Day Challenge",
    "AI Plan Generator": "AI Plan Generator",
    "3D Exercises Library": "3D Exercises Library",
    "Cuntooyinka (Meals)": "Meals & Nutrition",
    "Meals": "Meals",
    "3D Body Scan": "3D Body Scan",
    "Analytics / Hormarka": "Analytics & Progress",
    "Analytics": "Analytics",
    "Diiwaanka / History": "History & Logs",
    "History": "History",
    "Admin Control": "Admin Control",
    "Upgrade To Pro": "Upgrade to Pro",
    "Settings & Profile": "Settings & Profile",
    "Settings": "Settings",
    "Profile": "Profile",
    "Log out": "Log Out",
    "Login": "Log In",
    "Sign Up": "Sign Up",
    "Signup": "Sign Up",
    "Welcome back": "Welcome back",
    "Daily Calories": "Daily Calories",
    "Daily Protein": "Daily Protein",
    "Workouts Logged": "Workouts Logged",
    "Workout Streak": "Workout Streak",
    "Recent Activity": "Recent Activity",
    "Track Your Progress": "Track Your Progress",
    "Save": "Save",
    "Cancel": "Cancel",
    "Edit": "Edit",
    "Delete": "Delete",
    "Weight": "Weight",
    "Height": "Height",
    "Target Weight": "Target Weight",
    "Fitness Goal": "Fitness Goal",
    "Activity Level": "Activity Level",
    "Fitness Level": "Fitness Level",
    "Experience Level": "Experience Level",
    "Age": "Age",
    "Gender": "Gender",
    "Chest": "Chest",
    "Back": "Back",
    "Shoulders": "Shoulders",
    "Arms": "Arms",
    "Legs": "Legs",
    "Abs / Core": "Abs / Core",
    "Cardio": "Cardio",
    "Squats": "Squats",
    "Push-Ups": "Push-Ups",
    "Bicep Curls": "Bicep Curls",
    "Shoulder Press": "Shoulder Press",
    "Lunges": "Lunges",
    "Plank": "Plank",
    "Sit-Ups": "Sit-Ups",
    "Lateral Raises": "Lateral Raises",
    "Deadlifts": "Deadlifts",
    "Language": "Language",
    "Start Camera": "Start Camera",
    "Stop Camera": "Stop Camera",
    "Good form!": "Good form!",
    "Adjust form": "Adjust form",
    "Completed Reps": "Completed Reps",
    "Days Completed": "Days Completed",
    "Current Streak": "Current Streak",
    "Upgrade": "Upgrade",
    "Pro Active": "Pro Active",
    "Free Tier": "Free Tier",
    "Voice Feedback": "Voice Feedback",
    "Reset Reps": "Reset Reps",
    "Calories": "Calories",
    "Protein": "Protein",
    "Carbs": "Carbs",
    "Fats": "Fats",
    "Nutrition": "Nutrition",
    "Workout": "Workout",
    "Exercises": "Exercises",
    "Add Meal": "Add Meal",
    "Add Workout": "Add Workout",
    "Log Weight": "Log Weight",
}

TRANSLATIONS_AR = {
    "Dashboard": "لوحة التحكم",
    "AI Coach": "مدرب الذكاء الاصطناعي",
    "AI Form Detection": "تحليل وضعية التمرين بالذكاء الاصطناعي",
    "90-Day Challenge": "تحدي الـ 90 يوماً",
    "AI Plan Generator": "منشئ الخطط الذكي",
    "3D Exercises Library": "مكتبة التمارين ثلاثية الأبعاد",
    "Cuntooyinka (Meals)": "الوجبات والتغذية",
    "Meals": "الوجبات",
    "3D Body Scan": "المسح ثلاثي الأبعاد للجسم",
    "Analytics / Hormarka": "التحليلات والتقدم",
    "Analytics": "التحليلات",
    "Diiwaanka / History": "السجل والتاريخ",
    "History": "السجل",
    "Admin Control": "لوحة الإدارة",
    "Upgrade To Pro": "الترقية إلى برو",
    "Settings & Profile": "الإعدادات والملف الشخصي",
    "Settings": "الإعدادات",
    "Profile": "الملف الشخصي",
    "Log out": "تسجيل الخروج",
    "Login": "تسجيل الدخول",
    "Sign Up": "إنشاء حساب",
    "Signup": "إنشاء حساب",
    "Welcome back": "مرحباً بعودتك",
    "Daily Calories": "السعرات اليومية",
    "Daily Protein": "البروتين اليومي",
    "Workouts Logged": "التمارين المسجلة",
    "Workout Streak": "سلسلة الالتزام بالتمارين",
    "Recent Activity": "النشاط الأخير",
    "Track Your Progress": "تتبع تقدمك الرياضي",
    "Save": "حفظ",
    "Cancel": "إلغاء",
    "Edit": "تعديل",
    "Delete": "حذف",
    "Weight": "الوزن",
    "Height": "الطول",
    "Target Weight": "الوزن المستهدف",
    "Fitness Goal": "الهدف الرياضي",
    "Activity Level": "مستوى النشاط",
    "Fitness Level": "مستوى اللياقة",
    "Experience Level": "مستوى الخبرة",
    "Age": "العمر",
    "Gender": "الجنس",
    "Chest": "الصدر",
    "Back": "الظهر",
    "Shoulders": "الأكتاف",
    "Arms": "الذراعين",
    "Legs": "الأرجل",
    "Abs / Core": "البطن والوسط",
    "Cardio": "كارديو",
    "Squats": "سكوات (القرفصاء)",
    "Push-Ups": "تمرين الضغط (Push-Ups)",
    "Bicep Curls": "بايسبس كيرل (Bicep Curls)",
    "Shoulder Press": "ضغط الأكتاف (Shoulder Press)",
    "Lunges": "طعنات الأرجل (Lunges)",
    "Plank": "بلانك (Plank)",
    "Sit-Ups": "تمارين البطن (Sit-Ups)",
    "Lateral Raises": "الرفرفة الجانبية (Lateral Raises)",
    "Deadlifts": "ديدليفت (Deadlifts)",
    "Language": "اللغة",
    "Start Camera": "تشغيل الكاميرا",
    "Stop Camera": "إيقاف الكاميرا",
    "Good form!": "وضعية ممتازة ومثالية!",
    "Adjust form": "يرجى تعديل الوضعية",
    "Completed Reps": "التكرارات المكتملة",
    "Days Completed": "الأيام المنجزة",
    "Current Streak": "السلسلة الحالية",
    "Upgrade": "ترقية",
    "Pro Active": "عضوية برو نشطة",
    "Free Tier": "المستوى المجاني",
    "Voice Feedback": "التوجيه الصوتي",
    "Reset Reps": "إعادة ضبط العداد",
    "Calories": "السعرات الحرارية",
    "Protein": "البروتين",
    "Carbs": "الكربوهيدرات",
    "Fats": "الدهون",
    "Nutrition": "التغذية",
    "Workout": "التمرين",
    "Exercises": "التمارين",
    "Add Meal": "إضافة وجبة",
    "Add Workout": "إضافة تمرين",
    "Log Weight": "تسجيل الوزن",
}

def main():
    locale_dir = BASE_DIR / 'locale'
    
    # 1. Somali
    so_po = locale_dir / 'so' / 'LC_MESSAGES' / 'django.po'
    so_mo = locale_dir / 'so' / 'LC_MESSAGES' / 'django.mo'
    generate_po(TRANSLATIONS_SO, so_po, 'so')
    generate_mo(TRANSLATIONS_SO, so_mo)
    print(f"Generated {so_po} and {so_mo}")
    
    # 2. English
    en_po = locale_dir / 'en' / 'LC_MESSAGES' / 'django.po'
    en_mo = locale_dir / 'en' / 'LC_MESSAGES' / 'django.mo'
    generate_po(TRANSLATIONS_EN, en_po, 'en')
    generate_mo(TRANSLATIONS_EN, en_mo)
    print(f"Generated {en_po} and {en_mo}")
    
    # 3. Arabic
    ar_po = locale_dir / 'ar' / 'LC_MESSAGES' / 'django.po'
    ar_mo = locale_dir / 'ar' / 'LC_MESSAGES' / 'django.mo'
    generate_po(TRANSLATIONS_AR, ar_po, 'ar')
    generate_mo(TRANSLATIONS_AR, ar_mo)
    print(f"Generated {ar_po} and {ar_mo}")

if __name__ == '__main__':
    main()
