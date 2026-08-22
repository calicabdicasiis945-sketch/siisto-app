import os
import json
import re

DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SYSTEM_COACH_INSTRUCTION = (
    "Waxaad tahay 'Siisto & Skillset AI' — Tababare Jimicsi, Caafimaad, Cunto iyo Nolosha (Elite AI Fitness & Health Coach) oo xirfad sare leh, caqli badan, qadarin badan leh oo ku hadla Af-Soomaali aad u dabiici ah, suugaan leh, casri ah oo nool (iyo English haddii lagu weydiiyo).\n\n"
    "HADAFFADAADA:\n"
    "1. Su'aal kasta oo lagu weydiiyo (Cunto, Miisaan kordhin/dhimis, Muruq dhisid, Supplements, Caafimaad, Barnaamij jimicsi, ama su'aalo guud), si qoto dheer, cilmiyeysan oo faahfaahsan uga jawaab.\n"
    "2. Marka qofku miisaanka wax ka weydiiyo, u faahfaahi Caloric Surplus/Deficit, xaddiga Proteinka maalinlaha ah, Jimicsiga ku habboon (Hypertrophy / Strength), iyo hurdada & biyaha.\n"
    "3. Jawaabta ka dhig mid nidaamsan oo leh:\n"
    "   - Salaan iyo dhiirrigelin diirran.\n"
    "   - Qodobbo cadcad (Bullet points) & Shax (Tables) haddii loo baahdo.\n"
    "   - Talooyin wax ku ool ah (Actionable Tips).\n"
    "   - Gabagabo dhiirrigelin leh.\n"
    "4. Weligaa ha isticmaalin turjumaad qaldan ama qallafsan. Isticmaal ereyo Soomaali ah oo dadku fahmaan."
)

MODELS_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash",
    "gemini-flash-latest"
]

def get_api_key():
    return os.environ.get("GEMINI_API_KEY") or DEFAULT_API_KEY

def get_genai_client():
    api_key = get_api_key()
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        return None

def ask_gemini(user_message, custom_system_prompt=None, is_pro=False):
    client = get_genai_client()
    
    if is_pro:
        system_prompt = custom_system_prompt or (
            "Waxaad tahay 'Siisto AI Elite Master Coach (VIP Pro)' — Tababare Jimicsi iyo Nafaqo oo heerka caalamiga ah ah, "
            "aad u caqli badan, xisaabiya Macros/Calories, bixiya jadwal jimicsi oo qoto dheer (Periodized Splits), "
            "talooyin ku saabsan muruq dhisid, dhimis miisaan, ka hortagga dhaawacyada, iyo farsamooyinka saxda ah. "
            "Ku hadal Af-Soomaali aad u dabiici ah, hufan, qadarin leh oo aan wax xuruuf ah ku khaldanayn. "
            "U habee jawaabta qaab markdown qurux badan leh (Cinwaanno, Bullet points, Shax/Tables haddii loo baahdo, iyo Talooyin toos ah)."
        )
    else:
        system_prompt = custom_system_prompt or (
            "Waxaad tahay 'Siisto Free AI Fitness Assistant' — Kaaliye fudud oo caawiya tababarka iyo cuntada. "
            "U jawaab si kooban, dhiirrigelin leh, oo Af-Soomaali sax ah oo dabiici ah ku qoran."
        )

    full_prompt = f"System Instruction:\n{system_prompt}\n\nUser Question:\n{user_message}"

    if client:
        for model_name in MODELS_PRIORITY:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as err:
                continue

    # Fallback to smart knowledge engine in case API is offline/rate-limited
    return get_smart_somali_fitness_response(user_message, is_pro)


def get_smart_somali_fitness_response(user_msg, is_pro=False):
    """
    High quality fallback knowledge engine ensuring articulate Somali responses without any corrupted text.
    """
    msg = user_msg.lower()
    
    if any(w in msg for w in ['muruq', 'kordhi', 'weight gain', 'bulk', 'cayil', 'weyneey']):
        if is_pro:
            return (
                "### 💎 Qorshaha Xirfadeed ee Muruq Dhisidda & Miisaan Kordhinta (VIP Pro Master Plan)\n\n"
                "Si aad miisaankaaga iyo muruqaaga u kordhiso si cilmiyeysan oo degdeg ah, raac 4-ta tiir ee ugu muhiimsan:\n\n"
                "#### 1. Xisaabinta Cuntada (Caloric Surplus & Macros)\n"
                "- **Caloric Surplus:** Ku dar **+300 ilaa +500 Calories** maalin kasta wax ka badan inta jirkaagu gubo (TDEE).\n"
                "- **Borotiinka:** Cun **1.8g - 2.2g oo Borotiin ah** halkii kiilo ee miisaankaaga (Tusaale: Haddii aad tahay 65kg = ~130g Borotiin maalin kasta).\n"
                "- **Karbohaydraytka & Dufanka Wanaagsan:** Bariis, Baasto, Boorash (Oats), Baradho, Saliid Saytuun, laws iyo Avokado si aad u hesho tamar xooggan.\n\n"
                "#### 2. Jadwalka Jimicsiga (Hypertrophy 4-Day Split)\n"
                "| Maalinta | Qaybta Muruqa | Jimicsiyada Muhiimka ah | Sets x Reps |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| Isniin | Upper Body (Xabadka & Garabka) | Bench Press, Incline Dumbbell Press, Overhead Press | 4 x 8-10 |\n"
                "| Talaado | Lower Body (Lugaha) | Squats, Romanian Deadlifts, Leg Press | 4 x 8-12 |\n"
                "| Khamiis | Back & Biceps (Dhabarka & Gacmaha) | Pull-ups, Barbell Rows, Bicep Curls | 4 x 10-12 |\n"
                "| Sabti | Legs & Shoulders | Lunges, Lateral Raises, Calf Raises | 3 x 12-15 |\n\n"
                "#### 3. Farsamada Saxda ah & Progressive Overload\n"
                "- Toddobaad kasta miisaanka yar ku kordhi (Progressive Overload).\n"
                "- Xakamee dhaqdhaqaaqa (2 ilbiriqsi hoos u dhac, 1 ilbiriqsi kor u qaadid).\n\n"
                "#### 4. Nasashada & Biyaha\n"
                "- Seexo **7-8 saacadood** habeenkii si muruqyadu u koraan una dhismaan.\n"
                "- Cab **3-4 litir** oo biyo ah maalin kasta."
            )
        else:
            return (
                "### 💪 Talooyinka Aasaasiga ah ee Muruq Dhisidda (Free Tier)\n\n"
                "1. **Cun Cunto Protein Badan:** Hilibka digaagga, ukunta, kalluunka, digirta iyo caanaha.\n"
                "2. **Jimicsiga Culus:** Isticmaal miisaanka kugu habboon, samee jimicsiyada waaweyn sida Squats, Bench Press, iyo Pull-ups.\n"
                "3. **Nasashada:** Hurdo 8 saacadood habeenkii si muruqu u koro.\n\n"
                "⭐ *Talo:* Si aad u hesho xisaab buuxda oo miisaankaaga ah iyo jadwal todobaadle ah, ku biir **Siisto Pro**!"
            )
            
    elif any(w in msg for w in ['dhim', 'calool', 'lose weight', 'baruur', 'fat loss', 'diet']):
        if is_pro:
            return (
                "### 💎 Qorshaha Xirfadeed ee Baruur Dhimista & Jarista Caloosha (VIP Pro Cut Plan)\n\n"
                "Si aad u gubto baruurta adigoo ilaashanaya muruqaaga:\n\n"
                "#### 1. Caloric Deficit (Dhimista Tamar-cuntada)\n"
                "- Jirkaaga ka jar **-300 ilaa -500 Calories** maalin kasta.\n"
                "- Kordhi borotiinka (**2.0g halkii kg**) si aanad u lumin muruqa inta aad miisaanka dhimayso.\n\n"
                "#### 2. Cuntooyinka La Iska Ilaaliyo & Kuwa Fiican\n"
                "- **Ka Fogow:** Cabitaannada sonkorta leh, cuntada saliidda badan leh, iyo cuntooyinka qasacadaysan.\n"
                "- **Ku Dadaal:** Khudaarta cagaaran, ukunta, digirta, digaagga la dubay, iyo biyaha badan (3.5L+).\n\n"
                "#### 3. Jimicsiga & Cardio-ga\n"
                "- **Weight Training:** Samee 3-4 maalmood toddobaadkii si aad u kordhiso metabolism-ka.\n"
                "- **Incline Walking / Zone 2 Cardio:** 25-30 daqiiqo socod xawaare dhexdhexaad ah leh tababarka kadib."
            )
        else:
            return (
                "### 🔥 Talooyinka Baruur Dhimista (Free Tier)\n\n"
                "1. **Iska Yaree Sonkorta:** Iska jooji soodhaha, shaaha sonkorta badan iyo cuntooyinka degdega ah.\n"
                "2. **Biyo Badan Cab:** Cab ugu yaraan 3 litir oo biyo ah maalin kasta.\n"
                "3. **Dhaqdhaqaaqa:** Maalin kasta soco ugu yaraan 8,000 - 10,000 oo talaabo.\n\n"
                "⭐ *Talo:* Hel qorshe cunto oo gaar ah adiga oo isticmaalaya **Siisto Pro**!"
            )
            
    else:
        if is_pro:
            return (
                f"### 💎 Siisto Pro AI Master Coach\n\n"
                f"Su'aashaada ku saabsan **'{user_msg}'** waa mid aad muhiim u ah.\n\n"
                f"- **Talo:** Si aad hadafkaaga u gaadho, ku xidh hab-dhaqan joogto ah, cun cunto isku dheellitiran, oo jimicsigaaga si sax ah u qabso.\n"
                f"- **Kaalmo Dheeraad ah:** I weydii wax ku saabsan qorshe cunto, jadwal jimicsi, ama farsamada saxda ah ee jimicsi gaar ah!"
            )
        else:
            return (
                f"### 🤖 Siisto AI Assistant\n\n"
                f"Waad ku mahadsan tahay su'aashaada: **'{user_msg}'**.\n\n"
                f"Si aad natiijo fiican u hesho, ku dadaal tababar joogto ah iyo cunto caafimaad leh. "
                f"Waxaad kaloo i weydiin kartaa talooyin ku saabsan miisaanka, muruq dhisidda, ama jadwalka jimicsiga."
            )



def estimate_macros_with_gemini(meal_name):
    """
    Returns dict: {'calories': int, 'protein': float, 'carbs': float, 'fats': float}
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
        except Exception as err:
            print(f"Macro estimation fallback: {err}")
            continue

    return defaults


def analyze_meal_photo_with_gemini(image_file):
    """
    Analyzes an uploaded food photo using Gemini Vision API.
    Returns: dict with name, calories, protein, carbs, fats, description, confidence
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
            "Analyze this food photograph. Identify the meal name and estimate the approximate nutritional values for the entire portion shown.\n"
            "Return ONLY a raw JSON object (no markdown quotes, no other text) with the following exact keys:\n"
            "{\n"
            '  "name": "Short Descriptive Meal Name in Somali or English",\n'
            '  "calories": 500,\n'
            '  "protein": 30.0,\n'
            '  "carbs": 45.0,\n'
            '  "fats": 15.0,\n'
            '  "description": "Brief description of identified ingredients"\n'
            "}"
        )

        client = get_genai_client()
        if client:
            try:
                from google.genai import types
                part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                for model_name in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
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
                    except Exception as me:
                        print(f"Gemini Vision model {model_name} error: {me}")
                        continue
            except Exception as e:
                print(f"Google GenAI vision error: {e}")

        # Fallback to google.generativeai if installed
        try:
            import google.generativeai as legacy_genai
            from PIL import Image
            import io
            legacy_genai.configure(api_key=get_api_key())
            img = Image.open(io.BytesIO(image_bytes))
            model = legacy_genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([prompt, img])
            if response and response.text:
                json_match = re.search(r'\{.*\}', response.text.strip(), re.DOTALL)
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
        except Exception as le:
            print(f"Legacy Gemini Vision fallback error: {le}")

    except Exception as general_e:
        print(f"analyze_meal_photo_with_gemini general error: {general_e}")

    return defaults