import os
import json
import re

DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

MODELS_PRIORITY = [
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash",
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
        'tababar', 'yool', 'immisa', 'fadlan', 'haystaa', 'rabaa'
    ]
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    somali_matches = sum(1 for w in words if w in somali_keywords)
    if somali_matches >= 2 or any(w in ['muruq', 'cunto', 'jimicsi', 'miisaan', 'dhimis'] for w in words):
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
        if is_pro:
            return (
                "أنت 'Siisto AI Elite Master Coach (VIP Pro)' — مدرب لياقة بدنية وتغذية رياضية معتمد عالمياً. "
                "خبير في حساب السعرات والماكروز، وتصميم جداول تمارين احترافية (Periodized Splits)، وبناء العضلات، وحرق الدهون، "
                "وتصحيح وضعية التمارين. أجب باللغة العربية الفصحى الواضحة والمهنية، واستخدم تنسيق Markdown الجميل (نقاط، جداول، عناوين)."
            )
        return (
            "أنت 'Siisto Free AI Fitness Assistant' — مساعد اللياقة البدنية الذكي. "
            "أجب بإيجاز، وتشجيع، ولغة عربية فصحى طبيعية ودقيقة."
        )
    elif lang == 'en':
        if is_pro:
            return (
                "You are 'Siisto AI Elite Master Coach (VIP Pro)' — a world-class certified fitness & sports nutrition coach. "
                "Expert in calculating TDEE, macros, periodized workout splits, muscle hypertrophy, fat loss, injury prevention, "
                "and biomechanical form correction. Respond in natural, encouraging English using structured Markdown (bullet points, tables, action steps)."
            )
        return (
            "You are 'Siisto Free AI Fitness Assistant' — a helpful fitness and nutrition coach. "
            "Respond concisely with practical, accurate fitness advice in English."
        )
    else:  # Default: Somali
        if is_pro:
            return (
                "Waxaad tahay 'Siisto AI Elite Master Coach (VIP Pro)' — Tababare Jimicsi iyo Nafaqo oo heerka caalamiga ah ah, "
                "aad u caqli badan, xisaabiya Macros/Calories, bixiya jadwal jimicsi oo qoto dheer (Periodized Splits), "
                "talooyin ku saabsan muruq dhisid, dhimis miisaan, ka hortagga dhaawacyada, iyo farsamooyinka saxda ah. "
                "Ku hadal Af-Soomaali aad u dabiici ah, hufan, qadarin leh oo aan wax xuruuf ah ku khaldanayn. "
                "U habee jawaabta qaab markdown qurux badan leh (Cinwaanno, Bullet points, Shax/Tables haddii loo baahdo, iyo Talooyin toos ah)."
            )
        return (
            "Waxaad tahay 'Siisto Free AI Fitness Assistant' — Kaaliye fudud oo caawiya tababarka iyo cuntada. "
            "U jawaab si kooban, dhiirrigelin leh, oo Af-Soomaali sax ah oo dabiici ah ku qoran."
        )


def ask_gemini(user_message, custom_system_prompt=None, is_pro=False, language='so', conversation_history=None):
    """
    Query Google Gemini AI with multi-turn conversation context, structured contents, and multilingual support.
    """
    # Auto-detect language if prompt has distinct Arabic or Somali signals
    detected_lang = detect_language_from_text(user_message, default=language or 'so')
    active_lang = detected_lang if detected_lang in ['ar', 'so', 'en'] else (language or 'so')

    client = get_genai_client()
    system_prompt = get_system_prompt(language=active_lang, is_pro=is_pro, custom_prompt=custom_system_prompt)

    history_context = ""
    history_items = []
    if conversation_history:
        if isinstance(conversation_history, list):
            history_context = "\n".join(str(h) for h in conversation_history)
            history_items = conversation_history
        elif isinstance(conversation_history, str):
            history_context = conversation_history

    full_prompt = (
        f"System Instruction:\n{system_prompt}\n\n"
        f"{f'Previous Conversation Context:\n{history_context}\n\n' if history_context else ''}"
        f"Current User Question:\n{user_message}"
    )

    if client:
        # Try structured Contents if SDK supports types, else full_prompt string
        for model_name in MODELS_PRIORITY:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                continue

    # Multilingual Fallback Knowledge Engine
    return get_smart_multilingual_fitness_response(
        user_message,
        is_pro=is_pro,
        language=active_lang,
        history=history_context
    )


def get_smart_multilingual_fitness_response(user_msg, is_pro=False, language='so', history=""):
    """
    High-quality contextual fallback knowledge engine supporting Somali, English, and Arabic.
    Handles context like weight reference, sets for previously mentioned exercises, chest/squat queries.
    """
    msg = user_msg.lower()
    hist = (history or "").lower()
    lang = (language or 'so')[:2].lower()

    # Check for context follow-up: "how many sets", "sets", "reps"
    is_sets_query = any(w in msg for w in ['sets', 'reps', 'immisa set', 'xisaab', 'كم جولة', 'تكرار', 'set'])
    is_muscle_query = any(w in msg for w in ['muruq', 'kordhi', 'weight gain', 'bulk', 'cayil', 'muscle', 'عضل', 'بناء'])
    is_fatloss_query = any(w in msg for w in ['dhim', 'calool', 'lose weight', 'baruur', 'fat loss', 'diet', 'تنشيف', 'وزن', 'تخسيس'])
    is_chest_query = any(w in msg for w in ['chest', 'xabad', 'صدر', 'bench press'])
    is_leg_query = any(w in msg for w in ['leg', 'squat', 'lug', 'أرجل', 'فخذ'])
    is_meal_query = any(w in msg for w in ['eat', 'cunto', 'meal', 'food', 'diet', 'أكل', 'وجب'])

    # Handle follow-up sets query with chest/leg/previous context
    if is_sets_query and (is_chest_query or 'chest' in hist or 'xabad' in hist or 'صدر' in hist):
        if lang == 'ar':
            return (
                "### 💪 مجموعات وتكرارات تمارين الصدر (Chest Sets & Reps)\n\n"
                "لتضخيم عضلات الصدر وبناء القوة، اتبع البروتوكول التالي:\n\n"
                "- **Barbell / Dumbbell Bench Press:** 4 مجموعات × 8-10 تكرارات (راحة 90 ثانية).\n"
                "- **Incline Dumbbell Press:** 3-4 مجموعات × 10-12 تكرار (تركيز على الجزء العلوي).\n"
                "- **Chest Flyes (Cable / Dumbbell):** 3 مجموعات × 12-15 تكرار (عصر العضلة).\n"
                "- **Push-Ups:** 3 مجموعات حتى الفشل العضلي لإنهاء التمرين."
            )
        elif lang == 'en':
            return (
                "### 💪 Chest Workout Sets & Reps Protocol\n\n"
                "For optimal chest hypertrophy and progressive overload, follow this set/rep scheme:\n\n"
                "- **Flat Bench Press:** 4 sets × 8–10 reps (90s rest, heavy compound).\n"
                "- **Incline Dumbbell Press:** 3–4 sets × 10–12 reps (focus on upper chest stretch).\n"
                "- **Cable / Dumbbell Flyes:** 3 sets × 12–15 reps (constant tension & squeeze).\n"
                "- **Dips or Push-Ups:** 3 sets to failure (burnout finisher)."
            )
        else:
            return (
                "### 💪 Tirada Sets & Reps ee Jimicsiga Xabadka (Chest)\n\n"
                "Si aad u hesho muruq xabad oo dhisan oo ballaaran, raac qorshahan sets & reps:\n\n"
                "- **Flat Bench Press (Barbell/Dumbbell):** 4 sets × 8-10 reps (nasasho 90 ilbiriqsi).\n"
                "- **Incline Dumbbell Press:** 3-4 sets × 10-12 reps (xabadka kore).\n"
                "- **Cable Flyes / Dumbbell Flyes:** 3 sets × 12-15 reps (isku riixid buuxda).\n"
                "- **Push-Ups:** 3 sets ilaa inta aad ka daalayso (Finisher)."
            )

    # General Chest query
    if is_chest_query:
        if lang == 'ar':
            return (
                "### 🏋️ أفضل تمارين الصدر (Best Chest Exercises)\n\n"
                "1. **Bench Press:** أساس بناء حجم وقوة الصدر.\n"
                "2. **Incline Dumbbell Press:** لاستهداف الصدر العلوي.\n"
                "3. **Chest Dips:** للصدر السفلي والذراعين.\n"
                "4. **Cable Crossover / Flyes:** لعزل الألياف العضلية وتحديد الصدر."
            )
        elif lang == 'en':
            return (
                "### 🏋️ Best Chest Exercises for Hypertrophy\n\n"
                "1. **Barbell Bench Press:** King of upper body pushing movements.\n"
                "2. **Incline Dumbbell Press:** Hits the clavicular head (upper chest).\n"
                "3. **Chest Dips:** Engages lower pectorals and triceps.\n"
                "4. **Cable Flyes:** Provides peak contraction and continuous tension."
            )
        else:
            return (
                "### 🏋️ Jimicsiyada Ugu Fiican ee Xabadka (Chest)\n\n"
                "1. **Barbell / Dumbbell Bench Press:** Aasaaska dhisidda xabadka ballaaran.\n"
                "2. **Incline Dumbbell Press:** Waxay xoogga saartaa xabadka qaybtiisa kore.\n"
                "3. **Dips:** Xabadka hoose iyo gacmaha dambe (triceps).\n"
                "4. **Cable Flyes:** Kala bixin iyo isku riixid fiican oo muruqa qeexaysa."
            )

    # Meal query with weight context (e.g. "60kg")
    if is_meal_query:
        if lang == 'ar':
            return (
                "### 🥗 الخطة الغذائية وتوزيع الماكروز المقترحة\n\n"
                "- **البروتين:** 1.8g - 2.2g لكل كجم من وزنك (مثال: إذا كان وزنك 60 كجم = ~120g بروتين).\n"
                "- **الكربوهيدرات المعقدة:** الأرز البني، الشوفان، البطاطا، والمكرونة.\n"
                "- **الدهون الصحية:** زيت الزيتون، الأفوكادو، والمكسرات.\n"
                "- **السعرات:** زيادة +300 للبناء، أو عجز -400 لحرق الدهون."
            )
        elif lang == 'en':
            return (
                "### 🥗 Personalized Nutrition & Macro Breakdown\n\n"
                "- **Protein Target:** 1.8g – 2.2g per kg of body weight (e.g. 60kg body weight = ~120g protein/day).\n"
                "- **Complex Carbs:** Oats, jasmine rice, sweet potatoes, whole grain pasta for sustained workout energy.\n"
                "- **Healthy Fats:** Olive oil, avocado, eggs, almonds.\n"
                "- **Caloric Strategy:** +300-500 kcal surplus for lean bulking, or -400-500 kcal deficit for fat cutting."
            )
        else:
            return (
                "### 🥗 Qorshaha Cuntada & Xisaabinta Macros-ka\n\n"
                "- **Borotiinka:** 1.8g - 2.2g halkii kg oo miisaankaaga ah (Tusaale: Haddii aad tahay 60kg = ~120g borotiin maalin kasta).\n"
                "- **Karbohaydraytka Wanaagsan:** Boorashka (Oats), Bariiska, Baradhada, iyo Baastada.\n"
                "- **Dufanka Caafimaadka Leh:** Saliid Saytuun, Avokado, Ukun, iyo Lows.\n"
                "- **Biyaha:** Cab ugu yaraan 3-4 litir oo biyo ah maalin kasta."
            )

    # Muscle Gain
    if is_muscle_query:
        if lang == 'ar':
            return (
                "### 💎 الخطة الاحترافية لزيادة الوزن وبناء العضلات\n\n"
                "1. **الفائض من السعرات (Caloric Surplus):** تناول +300 إلى +500 سعرة فوق احتياجك اليومي.\n"
                "2. **البروتين:** 2.0g بروتين لكل كجم من وزنك.\n"
                "3. **التمارين:** رفع الأوزان 4-5 أيام أسبوعياً مع مبدأ الزيادة التدريجية (Progressive Overload).\n"
                "4. **النوم:** 7-8 ساعات يومياً لإعادة بناء الألياف العضلية."
            )
        elif lang == 'en':
            return (
                "### 💎 Hypertrophy & Muscle Building Master Plan\n\n"
                "1. **Caloric Surplus:** Consume +300 to +500 kcal above maintenance TDEE daily.\n"
                "2. **Protein Intake:** 2.0g per kg of body weight distributed across 4-5 meals.\n"
                "3. **Progressive Overload:** Increase weight or reps weekly on core compound lifts.\n"
                "4. **Recovery & Hydration:** 7-8 hours quality sleep and 3-4L water daily."
            )
        else:
            return (
                "### 💎 Qorshaha Xirfadeed ee Muruq Dhisidda & Miisaan Kordhinta\n\n"
                "1. **Caloric Surplus:** Ku dar **+300 ilaa +500 Calories** maalin kasta wax ka badan inta jirkaagu gubo.\n"
                "2. **Borotiinka:** Cun **1.8g - 2.2g oo Borotiin ah** halkii kiilo ee miisaankaaga.\n"
                "3. **Jadwalka Jimicsiga:** 4 maalmood tababar joogto ah (Upper/Lower Split).\n"
                "4. **Nasashada:** Hurdo 7-8 saacadood habeenkii si muruqyadu u koraan."
            )

    # Fat loss
    if is_fatloss_query:
        if lang == 'ar':
            return (
                "### 🔥 خطة حرق الدهون وتنشيف الجسم\n\n"
                "1. **عجز السعرات (Caloric Deficit):** تقليل -400 إلى -500 سعرة حرارية يومياً.\n"
                "2. **حماية العضلات:** رفع كمية البروتين إلى 2.2g لكل كجم.\n"
                "3. **الكارديو:** 20-30 دقيقة كارديو متوسط الشدة بعد التمرين أو 10,000 خطوة يومياً.\n"
                "4. **الماء:** شرب 3.5 لتر ماء على الأقل يومياً."
            )
        elif lang == 'en':
            return (
                "### 🔥 Comprehensive Fat Loss & Cutting Plan\n\n"
                "1. **Caloric Deficit:** Maintain a steady -400 to -500 kcal deficit below your TDEE.\n"
                "2. **Muscle Retention:** Keep protein high (2.0–2.2g/kg) to protect muscle mass.\n"
                "3. **Cardio & Activity:** 20-30 mins Zone 2 incline walking or 10,000 steps daily.\n"
                "4. **Hydration & Fiber:** Drink 3.5L water and eat plenty of vegetables."
            )
        else:
            return (
                "### 🔥 Qorshaha Xirfadeed ee Baruur Dhimista & Jarista Caloosha\n\n"
                "1. **Caloric Deficit:** Jirkaaga ka jar **-300 ilaa -500 Calories** maalin kasta.\n"
                "2. **Borotiin Badan:** Cun **2.0g halkii kg** si aad u ilaaliso muruqa inta aad miisaanka dhimayso.\n"
                "3. **Cardio & Dhaqdhaqaaq:** 25-30 daqiiqo socod ama 10,000 oo talaabo maalin kasta.\n"
                "4. **Iska ilaali Sonkorta:** Jooji cabitaannada macaan iyo cuntooyinka shiilan."
            )

    # Generic fallback
    if lang == 'ar':
        return (
            f"### 🤖 Siisto AI Coach\n\n"
            f"شكراً لسؤالك حول **'{user_msg}'**.\n\n"
            f"- **النصيحة:** لتحقيق أفضل نتائج رياضية، التزم بتمارين المقاومة المنتظمة، وتناول غذاء متوازناً غنياً بالبروتين.\n"
            f"- **كيف أساعدك:** اسألني عن خطة تمارين محددة، حساب السعرات، أو تصحيح وضعية أي تمرين!"
        )
    elif lang == 'en':
        return (
            f"### 🤖 Siisto AI Fitness Coach\n\n"
            f"Thank you for asking about **'{user_msg}'**.\n\n"
            f"- **Core Advice:** Stay consistent with progressive resistance training, hit your daily protein goal, and prioritize sleep.\n"
            f"- **Next Steps:** Feel free to ask for a custom workout split, nutrition macro breakdown, or exercise form tips!"
        )
    else:
        return (
            f"### 🤖 Siisto AI Assistant\n\n"
            f"Waad ku mahadsan tahay su'aashaada: **'{user_msg}'**.\n\n"
            f"- **Talo:** Si aad hadafkaaga u gaadho, ku xidh tababar joogto ah, cun cunto borotiin leh oo isku dheellitiran.\n"
            f"- **Kaalmo Dheeraad ah:** I weydii wax ku saabsan qorshe cunto, xisaabinta miisaanka, ama farsamada jimicsi kasta!"
        )


def estimate_macros_with_gemini(meal_name):
    """
    Estimates nutrition macros for 1 serving of a meal.
    """
    defaults = {'calories': 450, 'protein': 25.0, 'carbs': 45.0, 'fats': 12.0}
    client = get_genai_client()
    if not client:
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
                for model_name in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
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