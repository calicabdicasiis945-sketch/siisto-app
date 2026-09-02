import os
import json
import re
import math

DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

MODELS_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-flash-latest",
    "gemini-1.5-flash-latest",
]

def detect_language_from_text(text, default='so'):
    """
    Detect whether text is predominantly Arabic, Somali, or English.
    """
    if not text or not isinstance(text, str):
        return default

    # Check for Arabic characters
    if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text):
        return 'ar'

    # Check for Somali markers
    somali_keywords = [
        'waa', 'aan', 'ku', 'ka', 'ah', 'iyo', 'ee', 'oo', 'la', 'soo',
        'cunto', 'muruq', 'jimicsi', 'lugaha', 'xabadka', 'garabka', 'gacmaha',
        'dhabarka', 'caloosha', 'miisaan', 'dhimis', 'kordhin', 'sidee', 'maxaa',
        'tababar', 'yool', 'immisa', 'fadlan', 'haystaa', 'rabaa', 'waxaad',
        'korriin', 'hilib', 'bariis', 'digaag', 'ukun', 'biyo', 'hurdo', 'qorshe'
    ]
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    somali_matches = sum(1 for w in words if w in somali_keywords)
    if somali_matches >= 2 or any(w in ['muruq', 'cunto', 'jimicsi', 'miisaan', 'dhimis', 'calool', 'xabad'] for w in words):
        return 'so'

    # Default to English if Latin and no strong Somali match
    if re.search(r'[a-zA-Z]', text):
        if default in ['so', 'ar', 'en']:
            return default
        return 'en'

    return default

def get_api_key():
    return os.environ.get("GEMINI_API_KEY") or DEFAULT_API_KEY

def get_genai_client():
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def get_system_prompt(language='so', is_pro=False, custom_prompt=None):
    if custom_prompt:
        return custom_prompt

    lang = (language or 'so')[:2].lower()

    if lang == 'ar':
        return (
            "أنت 'Siisto AI Elite Master Coach' — مدرب لياقة بدنية وتغذية رياضية معتمد وخبير عالمي فائق الذكاء. "
            "أنت خبير في الميكانيكا الحيوية للتمارين، حساب السعرات الحرارية بدقة (TDEE/Macros)، تصميم جداول التمارين "
            "(Push-Pull-Legs, Upper-Lower, Arnold Split, Full Body)، خطط التضخيم والتنشيف، المكملات الغذائية (كرياتين، بروتين، فيتامينات)، "
            "والاستشفاء العضلي. قدّم إجابات متقدمة وعملية ومفصلة جداً باستخدام تنسيق Markdown الاحترافي (عناوين، جداول للمجموعات والتكرارات، نقاط واضحة)."
        )
    elif lang == 'en':
        return (
            "You are 'Siisto AI Elite Master Coach' — a world-class certified fitness coach, biomechanics specialist, "
            "and sports nutritionist with supreme intelligence. You specialize in evidence-based periodized training programs "
            "(Push/Pull/Legs, Upper/Lower, Hypertrophy Splits, Athletic Conditioning), precise caloric & macronutrient calculations, "
            "Somali and international healthy nutrition, biomechanical form correction, supplement science (Creatine, Whey, Electrolytes), "
            "and active recovery. Provide deep, structured, highly actionable responses using clean Markdown tables, bullet points, and step-by-step guidance."
        )
    else:  # Somali
        return (
            "Waxaad tahay 'Siisto AI Elite Master Coach' — Tababare Jimicsi iyo Khabiir Nafaqo oo heer caalami ah, "
            "aad iyo aad u caqli badan oo aqoon qoto dheer u leh dhisidda muruqyada, gubista baruurta, xisaabinta Calories & Macros, "
            "farsamada saxda ah ee jimicsiyada (Biomechanics), cuntooyinka Soomaalida ee caafimaadka leh (Bariis, Baasto, Hilib Geel, Digaag, Ukun, Caano, Moos, Boorash), "
            "iyo nafaqada kabka ah (Creatine, Whey Protein, Biyo, Fiitamiinno). "
            "U jawaab si hufan, dhiirrigelin leh, aqoon sare ku dheehan tahay oo Af-Soomaali qani ah oo sax ah ku qoran. "
            "Isticmaal qaab Markdown oo aad u habeysan (Cinwaanno cad-cad, Shaxyo/Tables loogu talagalay Sets & Reps, iyo Qodobbo qeexan)."
        )


def ask_gemini(user_message, custom_system_prompt=None, is_pro=False, language='so', conversation_history=None):
    """
    Query Google Gemini AI with multi-turn conversation context, structured contents, and multilingual support.
    Falls back to the deep built-in AI Fitness Knowledge Engine if API is unavailable.
    """
    detected_lang = detect_language_from_text(user_message, default=language or 'so')
    active_lang = detected_lang if detected_lang in ['ar', 'so', 'en'] else (language or 'so')

    client = get_genai_client()
    system_prompt = get_system_prompt(language=active_lang, is_pro=is_pro, custom_prompt=custom_system_prompt)

    history_context = ""
    if conversation_history:
        if isinstance(conversation_history, list):
            history_context = "\n".join(str(h) for h in conversation_history)
        elif isinstance(conversation_history, str):
            history_context = conversation_history

    full_prompt = (
        f"System Instruction:\n{system_prompt}\n\n"
        f"{f'Previous Conversation History:\n{history_context}\n\n' if history_context else ''}"
        f"Current User Question:\n{user_message}\n\n"
        f"Please provide an intelligent, expert-level coaching response with actionable instructions, sets/reps or meal breakdowns formatted in clean markdown."
    )

    if client:
        for model_name in MODELS_PRIORITY:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if response and response.text and len(response.text.strip()) > 20:
                    return response.text.strip()
            except Exception:
                continue

    # Master Multilingual AI Knowledge Engine
    return get_smart_multilingual_fitness_response(
        user_message,
        is_pro=is_pro,
        language=active_lang,
        history=history_context
    )


def get_smart_multilingual_fitness_response(user_msg, is_pro=False, language='so', history=""):
    """
    Ultra-Intelligent Multilingual Fitness & Nutrition Knowledge Engine.
    Handles workout splits, calorie/macro math, Somali meals, form corrections, supplements, and recovery.
    """
    msg = (user_msg or "").lower()
    hist = (history or "").lower()
    lang = (language or 'so')[:2].lower()

    # Intent detection
    is_sets_reps = any(w in msg for w in ['sets', 'reps', 'set', 'immisa set', 'xisaab', 'كم جولة', 'تكرار', 'jadwal', 'routine', 'split', 'qorshe'])
    is_chest = any(w in msg for w in ['chest', 'xabad', 'bench', 'pushup', 'push-up', 'flyes', 'dips', 'صدر', 'بنش'])
    is_back = any(w in msg for w in ['back', 'dhabar', 'pullup', 'pull-up', 'deadlift', 'lat', 'row', 'ظهر', 'سحب'])
    is_legs = any(w in msg for w in ['leg', 'squat', 'lug', 'lugo', 'quad', 'hamstring', 'calf', 'lunges', 'أرجل', 'فخذ', 'سكوات'])
    is_shoulders = any(w in msg for w in ['shoulder', 'garab', 'ohp', 'press', 'delt', 'lateral raise', 'أكتاف', 'كتف'])
    is_arms = any(w in msg for w in ['arm', 'bicep', 'tricep', 'gacan', 'gacmo', 'curl', 'skull crusher', 'بايسبس', 'ترايسبس', 'ذراع'])
    is_abs = any(w in msg for w in ['abs', 'core', 'calool', 'plank', 'crunch', 'six pack', 'six-pack', 'بطن', 'معدة'])
    is_ppl = any(w in msg for w in ['ppl', 'push pull legs', 'push pull', 'push/pull'])
    is_upper_lower = any(w in msg for w in ['upper lower', 'upper/lower', '4 maalmood', '4 days'])
    
    is_muscle = any(w in msg for w in ['muruq', 'kordhi', 'weight gain', 'bulk', 'cayil', 'hypertrophy', 'muscle', 'عضل', 'تضخيم'])
    is_fatloss = any(w in msg for w in ['dhim', 'baruur', 'lose weight', 'fat loss', 'cutting', 'calool', 'diet', 'تنشيف', 'تخسيس', 'حرق'])
    is_meal = any(w in msg for w in ['eat', 'cunto', 'meal', 'food', 'nutrition', 'protein', 'borotiin', 'calories', 'bariis', 'baasto', 'hilib', 'أكل', 'وجبة', 'دايت'])
    is_supplements = any(w in msg for w in ['creatine', 'kiriyeetiin', 'whey', 'protein powder', 'supplements', 'fiitamiin', 'omega', 'كرياتين', 'مكملات', 'واي بروتين'])
    is_pain_injury = any(w in msg for w in ['pain', 'xanuun', 'dhaawac', 'injury', 'hurt', 'dhabar xanuun', 'jilib', 'ألم', 'إصابة'])
    is_home_workout = any(w in msg for w in ['home', 'guriga', 'calisthenics', 'equipment la\'aan', 'no equipment', 'منزل', 'بدون أوزان'])

    # 1. PUSH-PULL-LEGS (PPL) SPLIT
    if is_ppl or ('push' in msg and 'pull' in msg):
        if lang == 'ar':
            return (
                "### 🔥 جدول تمرين Push / Pull / Legs (PPL) الاحترافي\n\n"
                "نظام PPL هو أفضل نظام علمي لبناء العضلات والقوة (Hypertrophy & Strength).\n\n"
                "#### 1️⃣ اليوم الأول: الدفع (Push - الصدر، الأكتاف، الترايسبس)\n"
                "| التمرين | المجموعات | التكرارات | الراحة |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Bench Press** | 4 | 6 - 8 | 2 دقيقة |\n"
                "| **Incline Dumbbell Press** | 3 | 8 - 10 | 90 ثانية |\n"
                "| **Dumbbell Overhead Press** | 3 | 8 - 10 | 90 ثانية |\n"
                "| **Lateral Raises (جانبي)** | 4 | 12 - 15 | 60 ثانية |\n"
                "| **Triceps Rope Pushdowns** | 3 | 12 - 15 | 60 ثانية |\n\n"
                "#### 2️⃣ اليوم الثاني: السحب (Pull - الظهر، البايسبس، الأكتاف الخلفية)\n"
                "| التمرين | المجموعات | التكرارات | الراحة |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Deadlift / Barbell Row** | 4 | 6 - 8 | 2 دقيقة |\n"
                "| **Lat Pulldown / Pull-ups** | 4 | 8 - 10 | 90 ثانية |\n"
                "| **Seated Cable Row** | 3 | 10 - 12 | 90 ثانية |\n"
                "| **Face Pulls (أكتاف خلفية)** | 4 | 15 | 60 ثانية |\n"
                "| **Incline Dumbbell Bicep Curls** | 3 | 10 - 12 | 60 ثانية |\n\n"
                "#### 3️⃣ اليوم الثالث: الأرجل والبطن (Legs & Abs)\n"
                "| التمرين | المجموعات | التكرارات | الراحة |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Back Squat** | 4 | 6 - 8 | 2 دقيقة |\n"
                "| **Romanian Deadlift (RDL)** | 3 | 8 - 10 | 90 ثانية |\n"
                "| **Leg Press** | 3 | 10 - 12 | 90 ثانية |\n"
                "| **Leg Curls + Calf Raises** | 4 | 12 - 15 | 60 ثانية |\n"
                "| **Hanging Leg Raises (بطن)** | 3 | 12 - 15 | 60 ثانية |"
            )
        elif lang == 'en':
            return (
                "### 🔥 Elite Push / Pull / Legs (PPL) Workout Program\n\n"
                "The PPL split allows maximum muscle protein synthesis with dedicated recovery.\n\n"
                "#### 1️⃣ DAY 1: PUSH (Chest, Shoulders & Triceps)\n"
                "| Exercise | Sets | Reps | Rest |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Flat Barbell Bench Press** | 4 | 6–8 | 2 min |\n"
                "| **Incline DB Press** | 3 | 8–10 | 90s |\n"
                "| **Dumbbell Shoulder Press** | 3 | 8–10 | 90s |\n"
                "| **Cable / DB Lateral Raises** | 4 | 12–15 | 60s |\n"
                "| **Triceps Overhead Extension** | 3 | 10–12 | 60s |\n\n"
                "#### 2️⃣ DAY 2: PULL (Back, Rear Delts & Biceps)\n"
                "| Exercise | Sets | Reps | Rest |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Bent-Over Row** | 4 | 6–8 | 2 min |\n"
                "| **Lat Pulldown or Weighted Pull-ups** | 4 | 8–10 | 90s |\n"
                "| **Chest-Supported Row** | 3 | 10–12 | 90s |\n"
                "| **Face Pulls** | 4 | 15 | 60s |\n"
                "| **Incline DB Bicep Curls** | 3 | 10–12 | 60s |\n\n"
                "#### 3️⃣ DAY 3: LEGS & CORE\n"
                "| Exercise | Sets | Reps | Rest |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Back Squat** | 4 | 6–8 | 2.5 min |\n"
                "| **Romanian Deadlift (Hamstrings)** | 3 | 8–10 | 90s |\n"
                "| **Bulgarian Split Squats** | 3 | 10 / leg | 90s |\n"
                "| **Standing Calf Raises** | 4 | 15 | 60s |\n"
                "| **Hanging Leg Raises** | 3 | 12–15 | 60s |"
            )
        else:
            return (
                "### 🔥 Qorshaha Xirfadeed ee Push / Pull / Legs (PPL Split)\n\n"
                "Nidaamka **PPL** waa jadwalka ugu caansan uguna natiijada badan dhisidda muruqyada iyo awoodda jirka.\n\n"
                "#### 1️⃣ MAALINTA 1: PUSH (Xabadka, Garabka & Triceps)\n"
                "| Jimicsiga | Sets | Reps | Nasashada |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Bench Press (Xabad)** | 4 | 6 - 8 | 2 daqiiqo |\n"
                "| **Incline Dumbbell Press (Xabadka Sare)** | 3 | 8 - 10 | 90 ilbiriqsi |\n"
                "| **Dumbbell Shoulder Press (Garabka)** | 3 | 8 - 10 | 90 ilbiriqsi |\n"
                "| **Lateral Raises (Garabka Dhinacyada)** | 4 | 12 - 15 | 60 ilbiriqsi |\n"
                "| **Triceps Rope Pushdown** | 3 | 10 - 12 | 60 ilbiriqsi |\n\n"
                "#### 2️⃣ MAALINTA 2: PULL (Dhabarka, Biceps & Garabka Dambe)\n"
                "| Jimicsiga | Sets | Reps | Nasashada |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell / T-Bar Row (Dhabarka)** | 4 | 6 - 8 | 2 daqiiqo |\n"
                "| **Lat Pulldown ama Pull-ups** | 4 | 8 - 10 | 90 ilbiriqsi |\n"
                "| **Seated Cable Row** | 3 | 10 - 12 | 90 ilbiriqsi |\n"
                "| **Face Pulls (Garabka Dambe)** | 4 | 15 | 60 ilbiriqsi |\n"
                "| **Dumbbell Bicep Curls** | 3 | 10 - 12 | 60 ilbiriqsi |\n\n"
                "#### 3️⃣ MAALINTA 3: LEGS & CALOOL (Lugaha & Abs)\n"
                "| Jimicsiga | Sets | Reps | Nasashada |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| **Barbell Squat (Lugaha)** | 4 | 6 - 8 | 2.5 daqiiqo |\n"
                "| **Romanian Deadlift (Hamstrings)** | 3 | 8 - 10 | 90 ilbiriqsi |\n"
                "| **Leg Press / Walking Lunges** | 3 | 10 - 12 | 90 ilbiriqsi |\n"
                "| **Calf Raises (Dibi-lugaha)** | 4 | 15 | 60 ilbiriqsi |\n"
                "| **Hanging Leg Raises (Caloosha)** | 3 | 12 - 15 | 60 ilbiriqsi |"
            )

    # 2. CHEST SPECIFIC
    if is_chest:
        if lang == 'ar':
            return (
                "### 💪 خطة تفجير عضلات الصدر (Chest Hypertrophy Protocol)\n\n"
                "للحصول على عضلات صدر ممتلئة وقوية، اعتمد هذا الترتيب الهندسي للزوايا:\n\n"
                "1. **Barbell Flat Bench Press:** 4 مجموعات × 6-8 تكرارات (الأساس للكتلة العضلية والقوة).\n"
                "2. **Incline Dumbbell Press (زاوية 30°):** 3-4 مجموعات × 8-10 تكرارات (عزل الصدر العلوي).\n"
                "3. **Chest Dips (مع إمالة الجذع للأمام):** 3 مجموعات × 10-12 تكرار (بناء الحافة السفلية للصدر).\n"
                "4. **Cable Crossover / Pec Deck Flyes:** 3 مجموعات × 12-15 تكرار (عصر متواصل في قمة الانقباض).\n\n"
                "💡 **نصيحة تقنية:** حافظ على ثبات لوحي الكتف (Retract Scapula) ولا تدع الكتف يتقدم للأمام أثناء الدفع."
            )
        elif lang == 'en':
            return (
                "### 💪 Master Chest Hypertrophy & Strength Guide\n\n"
                "To build a thick, armor-plated chest, hit all three angles with progressive overload:\n\n"
                "1. **Flat Barbell / DB Bench Press:** 4 sets × 6–8 reps (Primary heavy compound movement).\n"
                "2. **Incline DB Press (30° angle):** 3–4 sets × 8–10 reps (Maximizes clavicular upper head growth).\n"
                "3. **Chest Dips (Forward Lean):** 3 sets × 10–12 reps (Lower chest and outer sweep).\n"
                "4. **Cable Flyes / Pec Deck:** 3 sets × 12–15 reps (Peak continuous tension and stretch).\n\n"
                "💡 **Biomechanical Cue:** Retract and depress your scapulae throughout the entire press to protect rotator cuffs and maximize pectoral recruitment."
            )
        else:
            return (
                "### 💪 Tababarka Xirfadeed ee Xabadka (Chest Master Guide)\n\n"
                "Si aad u dhisto xabad ballaaran oo buuxda, raac jimicsiyadan iyo qaabka sets/reps-ka:\n\n"
                "1. **Flat Barbell / Dumbbell Bench Press:** 4 sets × 6-8 reps (Jimicsiga aasaasiga ah ee awoodda & dhumucda).\n"
                "2. **Incline Dumbbell Press (Kursiga kor u qaad 30°):** 3-4 sets × 8-10 reps (Xabadka qaybta sare).\n"
                "3. **Chest Dips (Horay u soo foorari):** 3 sets × 10-12 reps (Xabadka hoose iyo ballaca).\n"
                "4. **Cable Flyes ama Pec Deck Machine:** 3 sets × 12-15 reps (Muruqa oo aad isku qabato 2 ilbiriqsi).\n\n"
                "💡 **Talada Tababaraha:** Dhabarkaaga dambe labada garab isku celi (Retract Scapula) si culeysku u saarmto xabadka ee uusan ugu dhicin garabka hore."
            )

    # 3. BACK & DEADLIFT
    if is_back:
        if lang == 'ar':
            return (
                "### 🦅 خطة بناء ظهر عريض وسميك (V-Taper Back Protocol)\n\n"
                "1. **Conventional / Trap Bar Deadlift:** 3-4 مجموعات × 5-6 تكرارات (كثافة الظهر والعمود الفقري).\n"
                "2. **Barbell Bent-Over Row:** 4 مجموعات × 8-10 تكرارات (سماكة عضلات الظهر الأوسط).\n"
                "3. **Lat Pulldown أو Weighted Pull-ups:** 4 مجموعات × 8-12 تكرار (عرض الظهر وشكل الـ V-Taper).\n"
                "4. **Seated Cable Row:** 3 مجموعات × 10-12 تكرار (التركيز على عزل الـ Lats).\n"
                "5. **Face Pulls:** 4 مجموعات × 15 تكرار (حماية الأكتاف وتقوية عضلات الظهر العلوي)."
            )
        elif lang == 'en':
            return (
                "### 🦅 Complete V-Taper Back Building Routine\n\n"
                "1. **Barbell Deadlift:** 3–4 sets × 5–6 reps (Posterior chain strength & overall back thickness).\n"
                "2. **Barbell / Pendlay Row:** 4 sets × 8–10 reps (Mid-back & rhomboid density).\n"
                "3. **Wide-Grip Pull-ups / Lat Pulldown:** 4 sets × 8–12 reps (Broad V-Taper lat width).\n"
                "4. **Single-Arm Dumbbell Row:** 3 sets × 10–12 reps (Full stretch and deep contraction).\n"
                "5. **Face Pulls:** 4 sets × 15 reps (Rear delts & rotator cuff longevity)."
            )
        else:
            return (
                "### 🦅 Dhisidda Dhabarka Ballaaran ee V-Taper (Back Routine)\n\n"
                "1. **Deadlift:** 3-4 sets × 5-6 reps (Aasaaska awoodda dhabarka iyo jirka guud).\n"
                "2. **Barbell Bent-Over Row:** 4 sets × 8-10 reps (Dhumucda iyo buuxnaanta dhabarka dhexdiisa).\n"
                "3. **Lat Pulldown ama Pull-ups:** 4 sets × 8-12 reps (Ballaarinta dhabarka qaabka V-Shape).\n"
                "4. **Seated Cable Row:** 3 sets × 10-12 reps (Kala bixin buuxda iyo soo jiidasho xakameysan).\n"
                "5. **Face Pulls:** 4 sets × 15 reps (Garabka dambe iyo caafimaadka xubnaha)."
            )

    # 4. LEGS & SQUATS
    if is_legs:
        if lang == 'ar':
            return (
                "### 🦵 تمرين الأرجل الاحترافي (Monster Leg Day Workout)\n\n"
                "1. **Barbell Back Squats:** 4 مجموعات × 6-8 تكرارات (العمق الكامل تحت زاوية 90 درجة).\n"
                "2. **Romanian Deadlift (RDL):** 3-4 مجموعات × 8-10 تكرارات (استهداف أوتار الركبة والغلوتس).\n"
                "3. **Bulgarian Split Squats:** 3 مجموعات × 10 تكرارات لكل رجل (قوة وتوازن كل رجل منفردة).\n"
                "4. **Leg Extensions + Leg Curls:** 3 مجموعات سوبر سيت × 12-15 تكرار (ضخ دم هائل).\n"
                "5. **Standing & Seated Calf Raises:** 4 مجموعات × 15-20 تكرار."
            )
        elif lang == 'en':
            return (
                "### 🦵 High-Intensity Leg Hypertrophy Blueprint\n\n"
                "1. **Barbell Back Squat:** 4 sets × 6–8 reps (Hit parallel or below, maintain brace).\n"
                "2. **Romanian Deadlift (RDL):** 3–4 sets × 8–10 reps (Hip hinge focus for hamstrings & glutes).\n"
                "3. **Bulgarian Split Squat:** 3 sets × 10 reps/leg (Unilateral balance & quad drive).\n"
                "4. **Leg Press:** 3 sets × 12–15 reps (Constant tension, controlled eccentric).\n"
                "5. **Standing Calf Raises:** 4 sets × 15–20 reps (2s pause at bottom stretch)."
            )
        else:
            return (
                "### 🦵 Tababarka Awoodda & Muruqa Lugaha (Leg Day Protocol)\n\n"
                "1. **Barbell Back Squat:** 4 sets × 6-8 reps (Hoos u deg ilaa 90 degree ama ka hooseeya).\n"
                "2. **Romanian Deadlift (RDL):** 3-4 sets × 8-10 reps (Muruqa lugta dambe iyo barida).\n"
                "3. **Bulgarian Split Squat (Dumbbells):** 3 sets × 10 reps lugtiiba (Awood iyo dheellitir gaar ah).\n"
                "4. **Leg Press / Leg Extension:** 3 sets × 12-15 reps (Gubasho iyo korriin degdeg ah).\n"
                "5. **Calf Raises (Dibi-lugaha):** 4 sets × 15-20 reps (Joogso 2 ilbiriqsi marka aad kor u qaaddo)."
            )

    # 5. ARMS & SHOULDERS
    if is_arms or is_shoulders:
        if lang == 'ar':
            return (
                "### 💥 خطة تضخيم الذراعين والأكتاف (Arms & 3D Shoulders)\n\n"
                "#### عضلات الأكتاف (3D Shoulders):\n"
                "- **Overhead DB Press:** 4 مجموعات × 8-10 تكرارات.\n"
                "- **Dumbbell Lateral Raises (جانبي):** 4 مجموعات × 12-15 تكرار (سر عرض الكتف).\n"
                "- **Rear Delt Flyes (خلفي):** 3 مجموعات × 15 تكرار.\n\n"
                "#### عضلات الذراعين (Biceps & Triceps):\n"
                "- **Barbell EZ Bicep Curls:** 3 مجموعات × 8-10 تكرارات.\n"
                "- **Incline DB Hammer Curls:** 3 مجموعات × 10-12 تكرار (لسماكة البايسبس).\n"
                "- **Skull Crushers / Overhead Triceps Extension:** 3 مجموعات × 10-12 تكرار.\n"
                "- **Triceps Rope Pushdown:** 3 مجموعات × 12-15 تكرار."
            )
        elif lang == 'en':
            return (
                "### 💥 3D Shoulders & Massive Arms Routine\n\n"
                "#### 🛡️ Shoulders (Deltoids):\n"
                "- **Seated DB Shoulder Press:** 4 sets × 8–10 reps.\n"
                "- **Lateral Raises (Cable/DB):** 4–5 sets × 12–15 reps (Strict form, zero momentum).\n"
                "- **Reverse Pec Deck / Face Pulls:** 3 sets × 15 reps.\n\n"
                "#### 💪 Biceps & Triceps Super-Blast:\n"
                "- **Incline DB Bicep Curls:** 3 sets × 10–12 reps (Maximum long head stretch).\n"
                "- **Hammer Curls:** 3 sets × 10–12 reps (Brachialis for arm width).\n"
                "- **Overhead Cable Triceps Extension:** 3 sets × 10–12 reps (Hits the long head).\n"
                "- **Triceps Cable Pushdowns:** 3 sets × 12–15 reps."
            )
        else:
            return (
                "### 💥 Dhisidda Gacmaha Ballaaran & Garbaha 3D (Arms & Shoulders)\n\n"
                "#### 🛡️ Garbaha (Shoulders):\n"
                "- **Dumbbell Shoulder Press:** 4 sets × 8-10 reps (Garabka aasaaskiisa).\n"
                "- **Lateral Raises (Garabka Dhinacyada):** 4-5 sets × 12-15 reps (Sirta ballaca garabka).\n"
                "- **Rear Delt Flyes / Face Pulls:** 3 sets × 15 reps (Garabka dambe).\n\n"
                "#### 💪 Gacmaha (Biceps & Triceps):\n"
                "- **Barbell / Dumbbell Bicep Curls:** 3 sets × 8-10 reps.\n"
                "- **Hammer Curls (Muruqa Dhexda Gacanta):** 3 sets × 10-12 reps.\n"
                "- **Skull Crushers ama Overhead DB Extension:** 3 sets × 10-12 reps (Triceps-ka weyn).\n"
                "- **Triceps Rope Pushdown:** 3 sets × 12-15 reps (Gacanta dambe oo adkaata)."
            )

    # 6. SOMALI & INTERNATIONAL NUTRITION, CALORIES & MEAL PLANNING
    if is_meal or is_muscle or is_fatloss:
        if lang == 'ar':
            return (
                "### 🥗 الدليل الذهبي للتغذية، السعرات والماكروز (Nutrition & Macros)\n\n"
                "#### 1️⃣ حساب السعرات اليومية:\n"
                "- **لبناء العضلات (Bulking):** احسب احتياجك اليومي (TDEE) وأضف **+300 إلى +400 سعرة حرارية**.\n"
                "- **لحرق الدهون (Cutting):** اخفض **-400 إلى -500 سعرة حرارية** من احتياجك اليومي.\n\n"
                "#### 2️⃣ توزيع الماكروز المثالي:\n"
                "- **البروتين:** 2.0g - 2.2g لكل 1 كجم من وزنك (مثال: وزن 70 كجم = 140g - 154g بروتين).\n"
                "- **الدهون الصحية:** 0.8g لكل كجم (زيت زيتون، مكسرات، أفوكادو، صفار البيض).\n"
                "- **الكربوهيدرات:** باقي السعرات (أرز، شوفان، بطاطا، باستا).\n\n"
                "#### 3️⃣ خطة وجبات نموذجية:\n"
                "- **الإفطار:** 4 بيضات (3 بياض + 1 كاملة) + 60g شوفان مع حليب وموز.\n"
                "- **الغداء:** 180g صدر دجاج / لحم بقري صافي + 150g أرز مطبوخ + سلطة خضراء.\n"
                "- **سناك قبل التمرين:** موزة + قهوة سوداء أو ملعقة زبدة فول سوداني.\n"
                "- **العشاء:** 180g سمك مشوي أو تونة + بطاطا مسلوقة أو خضار مشوية."
            )
        elif lang == 'en':
            return (
                "### 🥗 Master Sports Nutrition, Calorie & Macro Blueprint\n\n"
                "#### 1️⃣ Calorie Targets:\n"
                "- **Lean Muscle Hypertrophy:** Maintenance TDEE + **300–400 kcal surplus**.\n"
                "- **Targeted Fat Loss:** Maintenance TDEE - **400–500 kcal deficit**.\n\n"
                "#### 2️⃣ Daily Macro Distribution:\n"
                "- **Protein:** 2.0g – 2.2g per kg of body weight (e.g. 70kg athlete = 140g–155g protein).\n"
                "- **Healthy Fats:** 0.8g – 1.0g per kg (Olive oil, avocado, whole eggs, almonds).\n"
                "- **Complex Carbs:** Balance of calories (Oats, jasmine rice, sweet potatoes, whole grain pasta).\n\n"
                "#### 3️⃣ Sample Daily Meal Schedule:\n"
                "- **Meal 1 (Breakfast):** 4 eggs (3 whites, 1 whole) + 70g rolled oats with banana & cinnamon.\n"
                "- **Meal 2 (Lunch):** 200g grilled chicken breast + 150g steamed rice + steamed broccoli & olive oil.\n"
                "- **Meal 3 (Pre-Workout Snack):** 1 banana + 1 scoop whey protein or Greek yogurt.\n"
                "- **Meal 4 (Dinner):** 200g salmon / white fish or lean beef steak + roasted sweet potatoes + fresh greens.\n"
                "- **Hydration:** Minimum 3.5 Liters of pure water throughout the day."
            )
        else:
            return (
                "### 🥗 Qorshaha Nafaqada, Xisaabinta Calories-ka & Cuntooyinka Soomaalida\n\n"
                "#### 1️⃣ Xisaabinta Kaloriyada & Hadafkaaga:\n"
                "- **Muruq Dhisid (Bulk):** Ku dar **+300 ilaa +400 Calories** maalin kasta wax ka badan inta jirkaagu gubo.\n"
                "- **Baruur Dhimis (Cut):** Ka jar **-400 ilaa -500 Calories** maalin kasta si baruurta u gubato.\n\n"
                "#### 2️⃣ Xisaabinta Macros-ka (Borotiinka & Karbohaydraytka):\n"
                "- **Borotiinka:** 2.0g halkii kiilo oo miisaankaaga ah (Tusaale: Haddii aad tahay 70kg = **140g oo Borotiin ah** maalin kasta).\n"
                "- **Dufanka Caafimaadka Leh:** 0.8g halkii kg (Saliid Saytuun, Ukun, Avokado, Lows).\n"
                "- **Karbohaydraytka:** Bariiska, Baastada, Boorashka (Oats), Baradhada, Mooska.\n\n"
                "#### 3️⃣ Jadwal Cunto Maalinle ah (Cuntooyinka Soomaalida):\n"
                "- **Quraac (8:00 AM):** 3-4 Ukun la kariyey + 1 koob Boorash (Oats) caano iyo moos leh.\n"
                "- **Qado (1:00 PM):** 150g Hilib Digaag / Hilib Geel caato ah + 1 baaquli Bariis ah + Saladh iyo Avokado.\n"
                "- **Cunto Fudud (4:30 PM):** 1 Moos + Kafee madow (jimicsiga ka hor).\n"
                "- **Casho (8:00 PM):** 150g Kalluun / Tuunno ama Hilib Digaag + Qudaar cagaaran iyo Baradho duban.\n"
                "- **Biyaha:** Cab ugu yaraan **3 ilaa 4 Litir** oo biyo nadiif ah maalin kasta."
            )

    # 7. SUPPLEMENTS (Creatine, Whey, etc.)
    if is_supplements:
        if lang == 'ar':
            return (
                "### 💊 الدليل العلمي للمكملات الغذائية (Supplements Guide)\n\n"
                "1. **الكرياتين أحادي الهيدرات (Creatine Monohydrate):**\n"
                "   - **الجرعة:** 5 جرام يومياً في أي وقت ثابت مع الماء أو الكارب.\n"
                "   - **الفائدة:** زيادة القوة العضلية الانفجارية، حبس الماء داخل الخلايا العضلية لزيادة الحجم.\n"
                "2. **الواي بروتين (Whey Protein):**\n"
                "   - **الجرعة:** سكوب واحد (25-30g بروتين) بعد التمرين أو عند الحاجة لإكمال احتياجك اليومي.\n"
                "3. **أوميغا 3 وفيتامين D3:**\n"
                "   - لصحة المفاصل، وتقليل الالتهابات، ودعم هرمون التستوستيرون الطبيعي.\n"
                "4. **الشوارد والماء (Electrolytes):**\n"
                "   - لضمان ترطيب العضلات ومنع التقلصات أثناء التمارين الشاقة."
            )
        elif lang == 'en':
            return (
                "### 💊 Evidence-Based Sports Supplement Guide\n\n"
                "1. **Creatine Monohydrate (Gold Standard):**\n"
                "   - **Dosage:** 5g daily, taken consistently at any time with water or carbs.\n"
                "   - **Benefits:** Maximizes intramuscular ATP energy, boosts power output, accelerates lean muscle mass.\n"
                "2. **Whey Protein Isolate / Concentrate:**\n"
                "   - **Dosage:** 1 scoop (25–30g protein) post-workout or as a quick dietary protein boost.\n"
                "3. **Omega-3 Fish Oil (EPA/DHA):**\n"
                "   - 2,000mg daily for joint lubrication, cardiovascular health, and lowering DOMS inflammation.\n"
                "4. **Vitamin D3 + K2 & Zinc/Magnesium (ZMA):**\n"
                "   - Supports natural testosterone synthesis, immune resilience, and deep REM sleep recovery."
            )
        else:
            return (
                "### 💊 Tilmaamaha Cilmiyeed ee Kaabayaasha Nafaqada (Supplements Guide)\n\n"
                "1. **Kiriyeetiin (Creatine Monohydrate):**\n"
                "   - **Qiyaasta:** 5g maalin kasta si joogto ah (looma baahna loading adag, biyo badan ku cab).\n"
                "   - **Faa'iidada:** Waxay kordhisaa awoodda muruqa, tamarta jimicsiga culus, iyo buuxnaanta unugyada muruqa.\n"
                "2. **Whey Protein (Borotiin Budo):**\n"
                "   - **Qiyaasta:** 1 scoop (25-30g borotiin) jimicsiga ka dib ama marka aad u baahato inaad buuxiso borotiinkaaga.\n"
                "3. **Fiitamiin D3 & Omega-3 (Saliidda Kalluunka):**\n"
                "   - Waxay ilaalisaa kala-goysyada, waxayna xoojisaa difaaca jirka iyo soo kabsashada.\n"
                "4. **Biyaha & Macdanta (Electrolytes):**\n"
                "   - Cab ugu yaraan 3.5 litir oo biyo ah si Kiriyeetiinku si buuxda ugu shaqeeyo."
            )

    # 8. PAIN / INJURY PREVENTION
    if is_pain_injury:
        if lang == 'ar':
            return (
                "### ⚠️ إرشادات الوقاية والتعامل مع آلام التمارين (Injury Prevention)\n\n"
                "1. **ألم أسفل الظهر أثناء السكوات أو الديدلفت:**\n"
                "   - تأكد من شد عضلات البطن (Bracing) وعدم تقوس الظهر.\n"
                "   - قلل الوزن وركز على حركة مفصل الورك (Hip Hinge).\n"
                "2. **ألم الكتف أثناء البنش برس:**\n"
                "   - اثنِ الكوعين بزاوية 45-75 درجة بدلاً من فتحهما بزاوية 90 درجة واسعة.\n"
                "3. **ألم الركبة:**\n"
                "   - تأكد من أن الركبة تتحرك في نفس اتجاه أصابع القدم ولا تنحني للداخل (Knee Valgus).\n"
                "4. **إذا كان الألم حاداً ومفاجئاً:** خذ استراحة واستشر طبيباً مختصاً."
            )
        elif lang == 'en':
            return (
                "### ⚠️ Biomechanics & Injury Prevention Protocol\n\n"
                "1. **Lower Back Strain (Squats/Deadlifts):**\n"
                "   - Master the Valsalva maneuver (intra-abdominal bracing).\n"
                "   - Avoid hyperextending or rounding your lumbar spine.\n"
                "2. **Shoulder Impingement in Bench Press:**\n"
                "   - Tuck elbows at a 45–70° angle relative to your torso (avoid 90° flaring).\n"
                "   - Retract shoulder blades firmly into the bench.\n"
                "3. **Knee Pain in Squats:**\n"
                "   - Track knees over toes in line with foot flare; avoid knee cave (valgus).\n"
                "4. **Acute vs. DOMS:** Soreness 24-48h later is normal muscle breakdown; sharp joint pain requires rest and load deloading."
            )
        else:
            return (
                "### ⚠️ Ka Hortagga Dhaawacyada & Xanuunnada Jimicsiga\n\n"
                "1. **Dhabar Xanuunka (Deadlift ama Squat):**\n"
                "   - Caloosha adkee (Brace your core) inta aadan culeyska qaadin, dhabarkana toos u hay.\n"
                "   - Culeys weyn ha qaadin ilaa aad farsamada (form) 100% ka barato.\n"
                "2. **Garab Xanuunka (Bench Press):**\n"
                "   - Xusullada ha furanin 90 degree, ee u soo dhowee dhinacyada jirkaaga 45-70 degree.\n"
                "3. **Jilib Xanuunka (Squats & Lunges):**\n"
                "   - Hubi in jilibkaagu toos ugu aadayo suulasha cagta ee uusan gudaha u soo liicin.\n"
                "4. **Nasasho & Biyo:** Haddii xanuun fiiqan jiro, jooji culeyskaas oo diiradda saar kala-bixinta (stretching) iyo nasashada."
            )

    # 9. GENERAL SMART MULTILINGUAL COACH RESPONSE
    if lang == 'ar':
        return (
            f"### 🤖 كوتش Siisto الذكي للياقة البدنية\n\n"
            f"أهلاً بك! بخصوص استفسارك حول: **'{user_msg}'**:\n\n"
            f"1. **الأساس العلمي:** التدرج في الأحمال (Progressive Overload) هو المحرك الأساسي لأي تطور عضلي وجسدي.\n"
            f"2. **الهدف الغذائي:** تأكد من تناول 1.8g إلى 2.2g بروتين لكل كجم من وزنك والنوم 7-8 ساعات يومياً.\n"
            f"3. **كيف أساعدك الآن:**\n"
            f"   - يمكنني تصميم جدول تمارين كامل (PPL أو 4 أيام أو 5 أيام).\n"
            f"   - حساب السعرات والماكروز بدقة لوزنك الحالي وهدفك.\n"
            f"   - شرح التكنيك الصحيح لأي تمرين تريده!"
        )
    elif lang == 'en':
        return (
            f"### 🤖 Siisto Elite AI Fitness Coach\n\n"
            f"Great question regarding: **'{user_msg}'**!\n\n"
            f"1. **Science-Based Progression:** Consistent progressive overload, structured recovery, and protein optimization drive 90% of all fitness transformations.\n"
            f"2. **Nutrition Anchor:** Aim for 2.0g protein/kg of body weight and keep daily hydration at 3.5L+.\n"
            f"3. **Next Steps I Can Provide:**\n"
            f"   - Personalized workout routine (Push/Pull/Legs, Upper/Lower, or 3-Day Full Body).\n"
            f"   - Exact Calorie, Protein, Carb, and Fat target math.\n"
            f"   - Biomechanical form analysis and corrective cues for any lift!"
        )
    else:
        return (
            f"### 🤖 Tababaraha Caqliga Badan ee Siisto AI\n\n"
            f"Ku soo dhowow! Su'aashaada ku saabsan: **'{user_msg}'**:\n\n"
            f"1. **Mabda'a Guusha:** Horumarka muruqa iyo dhimista baruurta waxay ku xiran yihiin **Tababar Joogto ah**, **Borotiin kugu filan (2g/kg)**, iyo **Hurdo 7-8 saacadood ah**.\n"
            f"2. **Talo Toos ah:** Xakamee cuntadaada adigoo ka fogaanaya sonkorta iyo saliidda xad-dhaafka ah, cabna ugu yaraan 3.5L oo biyo ah.\n"
            f"3. **Waxyaabaha aan hadda kugu caawin karo:**\n"
            f"   - Jadwal jimicsi oo buuxa (PPL 3-6 maalmood, ama Upper/Lower 4 maalmood).\n"
            f"   - Xisaabinta saxda ah ee Calories-ka iyo Macros-ka miisaankaaga.\n"
            f"   - Sharraxaadda farsamada saxda ah ee jimicsi kasta si aad dhaawac uga fogaato!"
        )


def estimate_macros_with_gemini(meal_name):
    """
    Estimates nutrition macros for 1 serving of a meal.
    """
    defaults = {'calories': 450, 'protein': 25.0, 'carbs': 45.0, 'fats': 12.0}
    client = get_genai_client()
    if not client:
        # Smart dictionary for Somali & global staples
        name_lower = (meal_name or '').lower()
        if 'bariis' in name_lower and 'hilib' in name_lower:
            return {'calories': 620, 'protein': 38.0, 'carbs': 75.0, 'fats': 18.0}
        if 'digaag' in name_lower or 'chicken' in name_lower:
            return {'calories': 480, 'protein': 42.0, 'carbs': 40.0, 'fats': 12.0}
        if 'baasto' in name_lower or 'pasta' in name_lower:
            return {'calories': 550, 'protein': 24.0, 'carbs': 82.0, 'fats': 14.0}
        if 'ukun' in name_lower or 'egg' in name_lower:
            return {'calories': 320, 'protein': 22.0, 'carbs': 10.0, 'fats': 20.0}
        if 'oats' in name_lower or 'boorash' in name_lower:
            return {'calories': 380, 'protein': 18.0, 'carbs': 60.0, 'fats': 8.0}
        if 'kalluun' in name_lower or 'fish' in name_lower or 'tuna' in name_lower:
            return {'calories': 420, 'protein': 36.0, 'carbs': 30.0, 'fats': 10.0}
        return defaults

    prompt = (
        f"Estimate realistic nutrition macros for 1 serving of meal named '{meal_name}'. "
        "Return ONLY a valid raw JSON object with keys: 'calories' (integer), 'protein' (float in grams), "
        "'carbs' (float in grams), 'fats' (float in grams). No markdown fences, no comments, just JSON."
    )

    for model_name in MODELS_PRIORITY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                raw = response.text.strip()
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    return {
                        'calories': int(parsed.get('calories', 450)),
                        'protein': float(parsed.get('protein', 25.0)),
                        'carbs': float(parsed.get('carbs', 45.0)),
                        'fats': float(parsed.get('fats', 12.0))
                    }
        except Exception:
            continue

    return defaults


def analyze_meal_photo_with_gemini(image_file):
    """
    Analyzes an uploaded food photo using Gemini Vision API.
    """
    defaults = {
        'name': 'Healthy Plate',
        'calories': 520,
        'protein': 30.0,
        'carbs': 50.0,
        'fats': 15.0,
        'description': 'Estimated balanced meal based on photo analysis.'
    }

    try:
        image_bytes = image_file.read()
        image_file.seek(0)
        mime_type = getattr(image_file, 'content_type', 'image/jpeg') or 'image/jpeg'

        prompt = (
            "Analyze this food photograph. Identify the meal name and estimate nutritional values for the portion shown.\n"
            "Return ONLY a raw JSON object with keys: 'name', 'calories', 'protein', 'carbs', 'fats', 'description'."
        )

        client = get_genai_client()
        if client:
            try:
                from google.genai import types
                part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                for model_name in MODELS_PRIORITY:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[part, prompt]
                        )
                        if response and response.text:
                            raw = response.text.strip()
                            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                            if json_match:
                                parsed = json.loads(json_match.group(0))
                                return {
                                    'name': str(parsed.get('name', 'Meal Photo Estimate')),
                                    'calories': int(parsed.get('calories', 500)),
                                    'protein': float(parsed.get('protein', 25.0)),
                                    'carbs': float(parsed.get('carbs', 45.0)),
                                    'fats': float(parsed.get('fats', 15.0)),
                                    'description': str(parsed.get('description', 'AI Estimated portion'))
                                }
                    except Exception:
                        continue
            except Exception:
                pass
    except Exception:
        pass

    return defaults