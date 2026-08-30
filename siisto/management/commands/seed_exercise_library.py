from django.core.management.base import BaseCommand
from siisto.models import ExerciseLibrary

EXERCISES_DATA = [
    # ==================== CHEST (8) ====================
    {
        "category": "Chest", "subcategory": "Chest", "name": "Bench Press",
        "target_muscle": "Mid & Overall Pectorals (Xabadka Guud)",
        "description": "Jimicsiga ugu caansan ee dhisidda xabadka buuxa iyo awoodda riixitaanka.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/pin/bench-press-3d-exercise-animation--123456789/",
        "default_duration": 15, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Dhabarka ku jiifso kursiga siman, gacmaha bar-bal ballac ku qabo, hoos u dhig ilaa xabadka taabto kadibna kor u riix."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Incline Bench Press",
        "target_muscle": "Clavicular Upper Chest (Xabadka Sare)",
        "description": "Kordhinta dhumucda iyo buuxnaanta xabadka sare.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=incline%20bench%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Kursiga geli 30-45 digrii, birta hoos ugu keen xabadka sare kadib kor u riix adoon suxullada xirin."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Decline Bench Press",
        "target_muscle": "Lower Pectorals (Xabadka Hoose)",
        "description": "Dhisidda iyo qeexidda xariiqda hoose ee muruqa xabadka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=decline%20bench%20press%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Kursiga hoos u foorara ku jiifso, si xakameysan hoos ugu dhig xabadka hoose kadibna kor u riix."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Dumbbell Press",
        "target_muscle": "Chest Stretch & Stabilization",
        "description": "Riixitaanka dumbbells-ka oo siinaya xabadka dhaqdhaqaaq qoto dheer.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20chest%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Dumbbell-yada hoos u keen ilaa feeraha dhinacooda, korna isugu keen adoo xabadka qabanaya."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Dumbbell Fly",
        "target_muscle": "Pectoral Stretch & Expansion",
        "description": "Kala bixidda xabadka oo ballaarisa qafiska feeraha.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20fly%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Suxullada yara qalooci, gacmaha dhinacyada u fur sida baalasha kadibna kor isugu soo jiid."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Cable Fly",
        "target_muscle": "Inner Chest & Squeeze Contraction",
        "description": "Qanjiirka xabadka dhexdiisa oo adkeeya muruqa xabadka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20fly%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Xadhkaha ka soo jiid labada dhinac, hore isugu keen adoo qanjiirinaya xabadka dhexdiisa."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Push Up",
        "target_muscle": "Chest, Front Delts & Core",
        "description": "Jimicsiga asalka ah ee miisaanka jirka lagu riixo ee xabadka.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=push%20up%203d%20animation",
        "default_duration": 10, "default_sets": 4, "default_reps": 15,
        "correct_form_instructions": "Jirka toosi, caloosha adkee, xabadka dhulka u dhowee kadibna kor isu riix."
    },
    {
        "category": "Chest", "subcategory": "Chest", "name": "Chest Dip",
        "target_muscle": "Lower Chest & Triceps",
        "description": "Hoos u daadashada iyo kor u riixitaanka birta ee xabadka hoose.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=chest%20dips%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Yara foorarso hore si culeyska u aado xabadka, hoos u deg ilaa 90 digrii kadibna kor isu riix."
    },

    # ==================== BACK (9) ====================
    {
        "category": "Back", "subcategory": "Back", "name": "Pull Up",
        "target_muscle": "Latissimus Dorsi (Lats) & Upper Back",
        "description": "Isku qaadista birta ee ballaarisa dhabarka sare.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=pull%20up%203d%20exercise",
        "default_duration": 12, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Gacmaha ballac ku qabo birta, dhabarka adkee, kor isu qaad ilaa garka birta ka sareeyo."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Chin Up",
        "target_muscle": "Lats & Biceps",
        "description": "Isku qaadista birta ee calaacalaha soo jeedaan oo dhabarka iyo gacanta dhista.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=chin%20up%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Calaacalaha xaggaaga ha soo eegaan, kor isu qaad adoo bicep-ka iyo dhabarka isku adeegsanaya."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Lat Pulldown",
        "target_muscle": "Lats Width (Ballaarinta Dhabarka)",
        "description": "Hoos u soo jiididda birta ballaaran ee dhabarka sare.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lat%20pulldown%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Birta ballac ku qabo, xabadka hore u soo saar, birta hoos ugu soo jiid xabadka sare."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Barbell Row",
        "target_muscle": "Mid Back & Rhomboids (Dhumucda Dhabarka)",
        "description": "Soo jiididda barbalka culus adoo foorara oo dhabarka dhumuc weyn siiya.",
        "image_url": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20row%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Foorarso 45 digrii dhabarkuna toos ha ahaado, birta xagga xuddunta u soo jiid suxulladana gadaal u mari."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Dumbbell Row",
        "target_muscle": "Unilateral Lats & Mid Back",
        "description": "Mid-mid u jiididda dumbbell culus oo kursiga lagu tiirsan yahay.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20row%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Gacanta iyo jilibka kursiga saar, dumbbell-ka dhinac kaga soo jiid xagga misigta adoo dhabarka qabanaya."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Seated Cable Row",
        "target_muscle": "Rhomboids, Lats & Mid-Back",
        "description": "Xadhigga fadhiga lagu soo jiido ee dhumucda dhabarka dhisaya.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=seated%20cable%20row%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Toos u fariiso dhabarku yuusan qaloocan, gacmaha xagga caloosha u soo jiid garbahana isku qabo."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "T-Bar Row",
        "target_muscle": "Upper & Mid Back Thickness",
        "description": "T-Bar culus oo lagu dhisayo dhumucda iyo xoogga dhabarka.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=t%20bar%20row%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Birta labada lugood dhexdooda ka qabo, dhabarka toosi, xabadka kor u qaad adoo birta soo jiidaya."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Deadlift",
        "target_muscle": "Entire Posterior Chain, Erector Spinae & Glutes",
        "description": "Jimicsiga aasaasiga ah ee qaadista culeyska dhulka yaalla.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=deadlift%203d%20exercise",
        "default_duration": 20, "default_sets": 4, "default_reps": 6,
        "correct_form_instructions": "Birta dhulka taal u dhowow, dhabarka toosi, lugaha iyo dhabarka isku mar ku kac adoon dhabarka qaloocin."
    },
    {
        "category": "Back", "subcategory": "Back", "name": "Straight Arm Pulldown",
        "target_muscle": "Lat Isolation & Teres Major",
        "description": "Kala bixidda iyo qanjiirka tooska ah ee muruqa lats-ka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=straight%20arm%20pulldown%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Gacmaha toosi suxulladana ha laabin, birta xadhigga ah hoos ugu riix ilaa bowdooyinka."
    },

    # ==================== SHOULDERS (10) ====================
    # Front Delts
    {
        "category": "Shoulders", "subcategory": "Front Delts", "name": "Front Raise",
        "target_muscle": "Anterior Deltoids (Garabka Hore)",
        "description": "Kor u qaadista dumbbell-ka xagga hore ee garabka hore.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=front%20raise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Dumbbell-yada horay ugu qaad ilaa heerka indhaha adoon jirka lulayn."
    },
    {
        "category": "Shoulders", "subcategory": "Front Delts", "name": "Arnold Press",
        "target_muscle": "Anterior & Lateral Deltoids",
        "description": "Wareejinta iyo riixitaanka dumbbell-yada ee qaabka Arnold Schwarzenegger.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=arnold%20press%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Calaacalaha xaggaaga ha u jeedaan xabadka hortiisa, kor u riix adoo wareejinaya calaacalaha hore."
    },
    # Side Delts
    {
        "category": "Shoulders", "subcategory": "Side Delts", "name": "Lateral Raise",
        "target_muscle": "Lateral Deltoids (Ballaarinta Garabka)",
        "description": "Dhinacyada u qaadista miisaanka ee ballaarisa garabka (V-Shape).",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lateral%20raise%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 15,
        "correct_form_instructions": "Gacmaha dhinacyada u qaad ilaa heerka garabka suxulladana wax yar qalooci."
    },
    {
        "category": "Shoulders", "subcategory": "Side Delts", "name": "Upright Row",
        "target_muscle": "Side Delts & Traps",
        "description": "Kor u soo jiididda birta tooska ah xagga garka.",
        "image_url": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=upright%20row%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Birta soo qaad adoo suxullada kor u qaadaya ilaa heerka xabadka sare."
    },
    # Rear Delts
    {
        "category": "Shoulders", "subcategory": "Rear Delts", "name": "Rear Delt Fly",
        "target_muscle": "Posterior Deltoids (Garabka Gadaale)",
        "description": "Kala bixidda garabka gadaale adoo foorara.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=rear%20delt%20fly%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Foorarso, dumbbell-yada gadaal iyo dhinacyada u fur adoo garabka gadaale isugu qabanaya."
    },
    {
        "category": "Shoulders", "subcategory": "Rear Delts", "name": "Face Pull",
        "target_muscle": "Rear Delts, Rotator Cuff & Upper Traps",
        "description": "Xadhigga xagga wajiga loo soo jiido ee saxaya booska garabka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=face%20pull%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 15,
        "correct_form_instructions": "Xadhigga xagga wejiga iyo dhegaha u soo jiid, suxulladana kor iyo gadaal u taag."
    },
    {
        "category": "Shoulders", "subcategory": "Rear Delts", "name": "Reverse Pec Deck",
        "target_muscle": "Posterior Deltoids Isolation",
        "description": "Mashiinka gadaal u riixa ee beegsada garabka dambe.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20pec%20deck%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Xabadka ku tiiri mashiinka, gacmaha gadaal u fur adoo garabka dambe cadaadinaya."
    },
    # Compound
    {
        "category": "Shoulders", "subcategory": "Compound", "name": "Overhead Press",
        "target_muscle": "Full Deltoid Complex & Triceps",
        "description": "Riixitaanka birta tooska ah ee madaxa kor looga qaado.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=overhead%20press%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Istaag toos, caloosha adkee, birta xabadka sare ka riix ilaa madaxa ka kor marto."
    },
    {
        "category": "Shoulders", "subcategory": "Compound", "name": "Dumbbell Shoulder Press",
        "target_muscle": "Front & Side Deltoids",
        "description": "Fadhiga lagu riixo dumbbells ee dhisaya garbo wareegsan.",
        "image_url": "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20shoulder%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Kursiga tooska ah fariiso, dumbbell-yada heerka garabka ka riix ilaa ay kor isugu yimaadaan."
    },
    {
        "category": "Shoulders", "subcategory": "Compound", "name": "Machine Shoulder Press",
        "target_muscle": "Shoulder Strength & Hypertrophy",
        "description": "Mashiinka garabka riixa ee aaminka ah.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=machine%20shoulder%20press%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Kursiga hagaaji, gacmaha qabo mashiinka kadibna kor u riix si xakameysan."
    },

    # ==================== ARMS (16) ====================
    # Biceps
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Barbell Curl",
        "target_muscle": "Biceps Brachii (Overall Bicep Mass)",
        "description": "Laabidda birta tooska ah ee dhisidda gacanta hore ee weyn.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20curl%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Suxullada feeraha ku dheji, birta kor u laab adoon jirka lulayn kadibna si tartiib ah u celi."
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Dumbbell Curl",
        "target_muscle": "Biceps Short & Long Head",
        "description": "Laabidda dumbbells-ka oo gacanta siiya buuxsanaan.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Mid-mid ama labada gacmood isku mar u laab adoo calaacasha kor u wareejinaya."
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Hammer Curl",
        "target_muscle": "Brachialis & Forearms (Dhumucda Gacanta)",
        "description": "Laabidda calaacalaha isu jeedaan ee dhisaya dhumucda gacanta.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=hammer%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Dumbbells-ka qabo sida dubbe (calaacalaha is hor jeedaan) kadibna kor u qaad."
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Concentration Curl",
        "target_muscle": "Biceps Peak Isolation",
        "description": "Fadhiga lagu go'doomiyo muruqa bicep-ka si uu buur u noqdo.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=concentration%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Suxulka ku celi bowdada gudaha, kor u laab dumbbell-ka adoo bicep-ka qanjiirinaya."
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Preacher Curl",
        "target_muscle": "Lower Bicep & Peak",
        "description": "Kursiga Preacher-ka ee go'doomiya gacanta hore.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=preacher%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Gacmaha saar barkinta Preacher-ka, birta EZ kor u soo laab adoon suxullada qaadin."
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Cable Curl",
        "target_muscle": "Constant Tension Biceps",
        "description": "Xadhigga hoose ee cadaadiska joogtada ah siiya gacanta.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Xadhigga hoose ka qabo, kor u soo laab adoo cadaadiska joogtada ah dareemaya."
    },
    # Triceps
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Tricep Pushdown",
        "target_muscle": "Lateral & Medial Triceps",
        "description": "Hoos u riixitaanka birta xadhigga ee gacanta dambe.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=tricep%20pushdown%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 12,
        "correct_form_instructions": "Suxullada feeraha ku dheji, birta tooska ah ama xadhigga hoos ugu riix ilaa gacantu toosto."
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Overhead Extension",
        "target_muscle": "Long Head of Triceps",
        "description": "Madaxa kor looga riixo miisaanka ee dhisaya dhabarka gacanta sare.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=tricep%20overhead%20extension%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Dumbbell-ka labada gacmood ku qabo madaxa gadaashiisa, kor u toosi gacmaha."
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Skull Crusher",
        "target_muscle": "Triceps Long & Medial Heads",
        "description": "Jiifka birta loogu celiyo wejiga ee dhisidda triceps xooggan.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=skull%20crusher%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Kursiga ku jiifso, birta EZ hoos ugu soo celi xagga wejiga sare kadibna kor u toosi."
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Close Grip Bench Press",
        "target_muscle": "Inner Triceps & Chest",
        "description": "Riixitaanka birta oo gacmaha la isu soo dhoweeyey.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=close%20grip%20bench%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Birta qabo masaafo garabka ka yar, hoos u dhig xabadka kadibna triceps-ka ku riix kor."
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Bench Dips",
        "target_muscle": "Bodyweight Tricep Focus",
        "description": "Kursiga lagu tiirsado ee lagu riixo gacanta dambe.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=bench%20dips%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Gacmaha dhabarka gadaashiisa kursiga saar, hoos u deg ilaa 90 digrii kadibna kor isu riix."
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Rope Pushdown",
        "target_muscle": "Triceps Horseshoe Lateral Peak",
        "description": "Xadhigga hoos loo riixo oo la kala bixiyo dhamaadka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=rope%20tricep%20pushdown%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Xadhigga hoos ugu riix adoo gunta hoose ku kala furaya gacmaha si triceps-ku u qanjiirmo."
    },
    # Forearms
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Wrist Curl",
        "target_muscle": "Forearm Flexors & Grip",
        "description": "Laabidda curcurka gacanta ee dhisaya horeeyaha gacanta.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=wrist%20curl%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Gacmaha bowdada saar calaacashu kor u jeeddo, curcurka kor iyo hoos u laab."
    },
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Reverse Wrist Curl",
        "target_muscle": "Forearm Extensors",
        "description": "Laabidda curcurka calaacasha oo hoos u jeedda.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20wrist%20curl%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Calaacasha hoos u jeedi, curcurka kor u qaad adoo horeeyaha gacanta kore cadaadinaya."
    },
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Farmer's Walk",
        "target_muscle": "Grip Strength, Forearms & Traps",
        "description": "Socodka adoo labada gacmood ku wada culeysyo culus.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=farmers%20walk%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 1,
        "correct_form_instructions": "Dumbbells culus gacmaha ku qabo, toos u soco tallaabooyin deggan adoo dhabarka toosinaya."
    },
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Reverse Curl",
        "target_muscle": "Brachioradialis & Forearms",
        "description": "Laabidda birta calaacalaha hoos u jeedaan.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Birta kor kaga qabo (calaacalaha hoos u jeedaan) kadibna kor u laab."
    },

    # ==================== LEGS (15) ====================
    # Quadriceps
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Squat",
        "target_muscle": "Quads, Glutes & Core (Boqorka Jimicsiyada)",
        "description": "Fariisashada iyo kicidda culeyska ee dhisidda awoodda lugaha.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20squat%203d",
        "default_duration": 18, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Lugaha ballac garabka la eg u fur, hoos u fariiso ilaa bowdooyinku siman yihiin dhabarkana toosi."
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Front Squat",
        "target_muscle": "Quad Isolation & Core Stability",
        "description": "Fariisashada birta xabadka hore saaran tahay.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=front%20squat%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 8,
        "correct_form_instructions": "Birta saar garabka hore suxulladana kor u taag, hoos u fariiso toos adoon dhabarka foorarin."
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Leg Press",
        "target_muscle": "Quadriceps Hypertrophy & Glutes",
        "description": "Riixitaanka mashiinka 45 digrii ee culeyska lugaha.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=leg%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 12,
        "correct_form_instructions": "Cagaha saar saxanka mashiinka, hoos u soo laab ilaa jilbuhu 90 digrii gaaraan kadibna kor u riix."
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Leg Extension",
        "target_muscle": "Rectus Femoris & Quad Teardrop",
        "description": "Fadhiga lagu toosiyo lugaha mashiinka ee go'doomiya bowdada hore.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=leg%20extension%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Mashiinka fariiso, lugaha kor u toosi adoo bowdada hore qanjiirinaya."
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Bulgarian Split Squat",
        "target_muscle": "Unilateral Quads & Glute Sculpting",
        "description": "Fariisashada hal lug oo lugta kale kursiga dambe saaran tahay.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=bulgarian%20split%20squat%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Hal lug dambe kursiga saar, lugta hore hoos ugu deg ilaa jilibku 90 digrii noqdo kadibna kor u kac."
    },
    # Hamstrings
    {
        "category": "Legs", "subcategory": "Hamstrings", "name": "Romanian Deadlift",
        "target_muscle": "Hamstrings & Glute-Ham Tie-In",
        "description": "Foorarsiga jilbaha yara qaloocan ee dhisaya dhabarka bowdada.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=romanian%20deadlift%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Misigta gadaal u riix dhabarka toosi, birta hoos u dhig ilaa jilibka hoostiisa kadibna bowdada gadaale ku kac."
    },
    {
        "category": "Legs", "subcategory": "Hamstrings", "name": "Leg Curl",
        "target_muscle": "Hamstring Bicep Femoris Isolation",
        "description": "Jiifka ama fadhiga lugaha loogu laabo mashiinka bowdada gadaale.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lying%20leg%20curl%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 12,
        "correct_form_instructions": "Caloosha ku jiifso mashiinka, lugaha xagga badhida u soo laab adoo bowdada dambe qabanaya."
    },
    {
        "category": "Legs", "subcategory": "Hamstrings", "name": "Good Morning",
        "target_muscle": "Hamstrings & Lower Back",
        "description": "Foorarsiga birta garabka dambe saaran tahay.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=good%20morning%20exercise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Birta garabka dambe saar, misigta gadaal u riix adoo dhabarka toosinaya kadibna kor u kac."
    },
    # Glutes
    {
        "category": "Legs", "subcategory": "Glutes", "name": "Hip Thrust",
        "target_muscle": "Gluteus Maximus (Dhisidda Badhida)",
        "description": "Riixitaanka misigta culeyska saaran yahay ee kursiga lagu tiirsan yahay.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20hip%20thrust%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 10,
        "correct_form_instructions": "Dhabarka sare kursiga ku tiiri, birta misigta saar, kor u riix misigta adoo badhida qanjiirinaya."
    },
    {
        "category": "Legs", "subcategory": "Glutes", "name": "Glute Bridge",
        "target_muscle": "Glutes & Core Activation",
        "description": "Kor u qaadista misigta adoo dhulka jiifa.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=glute%20bridge%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Dhulka ku jiifso jilbuhuna laaban yihiin, misigta kor u qaad adoo ciribta dhulka ku riixaya."
    },
    {
        "category": "Legs", "subcategory": "Glutes", "name": "Cable Kickback",
        "target_muscle": "Glute Isolation & Upper Glutes",
        "description": "Gadaal u laaditaanka xadhigga lugta ku xiran.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20kickback%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Xadhigga canqowga ku xir, lugta gadaal toos ugu laad adoo badhida qanjiirinaya."
    },
    # Calves
    {
        "category": "Legs", "subcategory": "Calves", "name": "Standing Calf Raise",
        "target_muscle": "Gastrocnemius (Kubka Sare)",
        "description": "Taagnida ciribta kor loogu qaado ee dhisidda kubka.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=standing%20calf%20raise%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 15,
        "correct_form_instructions": "Suulasha ku istaag meel sarreysa, ciribta kor u qaad intii suurtagal ah kadibna hoos u deg si buuxda."
    },
    {
        "category": "Legs", "subcategory": "Calves", "name": "Seated Calf Raise",
        "target_muscle": "Soleus (Kubka Hoose)",
        "description": "Fadhiga lagu qaado culeyska kubka.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=seated%20calf%20raise%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 15,
        "correct_form_instructions": "Fariiso barkintana jilbaha saar, ciribta kor u qaad adoo kubka hoose cadaadinaya."
    },
    {
        "category": "Legs", "subcategory": "Calves", "name": "Donkey Calf Raise",
        "target_muscle": "Deep Calf Hypertrophy",
        "description": "Foorarsiga lagu qaado kubka ee siinaya kala bixin weyn.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=donkey%20calf%20raise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Foorarso 90 digrii, ciribta kor u taag adoo kubka si buuxda u qanjiirinaya."
    },

    # ==================== ABS/CORE (13) ====================
    # Upper Abs
    {
        "category": "Abs / Core", "subcategory": "Upper Abs", "name": "Crunch",
        "target_muscle": "Upper Rectus Abdominis (Caloosha Sare)",
        "description": "Laabidda caloosha sare ee samaynta xariiqyada six-pack.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=crunch%20exercise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 20,
        "correct_form_instructions": "Dhabarka ku jiifso jilbaha laab, garbaha dhulka ka qaad adoo caloosha sare cadaadinaya."
    },
    {
        "category": "Abs / Core", "subcategory": "Upper Abs", "name": "Cable Crunch",
        "target_muscle": "Weighted Upper Abs",
        "description": "Jilba-joogsiga xadhigga caloosha lagu soo laabo.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20crunch%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Jilbaha ku fariiso xadhigga madaxa agtiisa ku qabo, caloosha hoos ugu laab xagga jilbaha."
    },
    {
        "category": "Abs / Core", "subcategory": "Upper Abs", "name": "Sit Up",
        "target_muscle": "Full Abdominal Wall & Hip Flexors",
        "description": "Fariisashada tooska ah ee jiifka laga kaco.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=sit%20up%20exercise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Jiifka ka kac ilaa aad toos u fariisato adoo caloosha adkeynaya."
    },
    # Lower Abs
    {
        "category": "Abs / Core", "subcategory": "Lower Abs", "name": "Leg Raise",
        "target_muscle": "Lower Rectus Abdominis (Caloosha Hoose)",
        "description": "Jiifka lugaha tooska ah kor loogu qaado ee caloosha hoose.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lying%20leg%20raise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Dhulka ku jiifso, lugaha toosi oo kor u qaad ilaa 90 digrii adoon dhabarka hoose ka qaadin dhulka."
    },
    {
        "category": "Abs / Core", "subcategory": "Lower Abs", "name": "Hanging Leg Raise",
        "target_muscle": "Lower Abs & Hip Strength",
        "description": "Lulashada birta lugaha kor loogu qaado ee caloosha adag.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=hanging%20leg%20raise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Birta ka laadlaadso, lugaha kor u qaad ilaa heerka misigta adoo caloosha hoose adkeynaya."
    },
    {
        "category": "Abs / Core", "subcategory": "Lower Abs", "name": "Reverse Crunch",
        "target_muscle": "Lower Abs Contraction",
        "description": "Misigta dhulka laga qaado adoo jiifa.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20crunch%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15,
        "correct_form_instructions": "Jilbaha laab oo xagga xabadka u soo jiid adoo misigta wax yar dhulka ka qaadaya."
    },
    # Obliques
    {
        "category": "Abs / Core", "subcategory": "Obliques", "name": "Russian Twist",
        "target_muscle": "Internal & External Obliques (Dhinacyada Caloosha)",
        "description": "Wareejinta jirka ee labada dhinac adoo fadhiya.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=russian%20twist%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 20,
        "correct_form_instructions": "Fariiso lugaha kor u yara qaad, gacmaha midig iyo bidix u leexi adoo dhexda wareejinaya."
    },
    {
        "category": "Abs / Core", "subcategory": "Obliques", "name": "Side Plank",
        "target_muscle": "Lateral Core Stability & Obliques",
        "description": "Dhinaca lagu taageero jirka ee adkeynta feeraha dhinacooda.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=side%20plank%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 1,
        "correct_form_instructions": "Hal suxul dhulka saar, jirka toosi oo kor u hay 30-45 ilbiriqsi dhinac kasta."
    },
    {
        "category": "Abs / Core", "subcategory": "Obliques", "name": "Bicycle Crunch",
        "target_muscle": "Obliques & Rectus Abdominis",
        "description": "Baaskiil wadidda jiifka ee isku xirta suxulka iyo jilibka iska soo horjeeda.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=bicycle%20crunch%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 20,
        "correct_form_instructions": "Suxulka midig ku taabo jilibka bidix, kadibna kan kale ku beddel adoo lugaha sida baaskiilka u wareejinaya."
    },
    # Core
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Plank",
        "target_muscle": "Transverse Abdominis & Deep Core",
        "description": "Haynta tooska ah ee jirka ee dhisidda dhexda birta ah.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=plank%20exercise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 1,
        "correct_form_instructions": "Suxullada iyo suulasha ku taagnaw, dhabarka iyo caloosha toos u adkee 60 ilbiriqsi."
    },
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Mountain Climber",
        "target_muscle": "Dynamic Core & Calorie Burn",
        "description": "Orodka booska push-up-ka ee adkeeya caloosha.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=mountain%20climber%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 30,
        "correct_form_instructions": "Booska push-up-ka gal, jilbaha mid-mid xagga xabadka ugu soo orod si degdeg ah."
    },
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Dead Bug",
        "target_muscle": "Deep Core Stability & Pelvic Control",
        "description": "Dhaqdhaqaaqa lidka ku ah ee gacmaha iyo lugaha adoo dhabarka u jiifa.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dead%20bug%20exercise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 12,
        "correct_form_instructions": "Dhabarka ku jiifso, gacanta midig iyo lugta bidix hoos u toosi isku mar adoon dhabarka ka qaadin dhulka."
    },
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Ab Wheel Rollout",
        "target_muscle": "Extreme Core Tension & Lats",
        "description": "Duubista giraanta caloosha ee hore loo sii riixo.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=ab%20wheel%20rollout%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10,
        "correct_form_instructions": "Jilbaha ku fariiso giraanta qabo, hore u duub adoo caloosha adkeynaya kadibna dib ugu soo celi."
    },

    # ==================== CARDIO (8) ====================
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Walking",
        "target_muscle": "Low Intensity Steady State (Socod)",
        "description": "Socodka caafimaadka qaba ee guba dufanka aaminka ah.",
        "image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=walking%20exercise%203d",
        "default_duration": 30, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Toos u soco, gacmaha lul, tallaabooyin deggan qaad 30-45 daqiiqo."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Running",
        "target_muscle": "High Calorie Burn (Orod)",
        "description": "Orodka degdegga ah ee adkeynta wadnaha iyo sambabada.",
        "image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=running%20exercise%203d",
        "default_duration": 20, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Orod xakameysan, cagaha hore ku deg, neefsasho joogto ah yeelo."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Treadmill",
        "target_muscle": "Cardiovascular Conditioning",
        "description": "Mashiinka orodka iyo socodka ee qolka jimicsiga.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=treadmill%20running%203d",
        "default_duration": 25, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Xawaaraha iyo leexada ku hagaaji heerkaaga, toos u orod ama u soco."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Cycling",
        "target_muscle": "Leg Endurance & Cardio (Baaskiil)",
        "description": "Wadida baaskiilka ee kordhisa adkeysiga lugaha.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cycling%20exercise%203d",
        "default_duration": 25, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Baaskiilka hagaaji, lugaha ku riix baydallada si wareegsan oo xakameysan."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Jump Rope",
        "target_muscle": "Agility & Calf & Fat Loss (Xadhig Bood)",
        "description": "Xadhig boodka degdegga ah ee guba baruurta badan.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=jump%20rope%203d%20animation",
        "default_duration": 15, "default_sets": 3, "default_reps": 100,
        "correct_form_instructions": "Suulasha ku bood, curcurrada gacanta ku wareeji xadhigga, jilbaha ha xirin."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Rowing Machine",
        "target_muscle": "Full Body Cardio & Back",
        "description": "Mashiinka doon-wadida ee tababara 85% murqaha jirka.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=rowing%20machine%203d",
        "default_duration": 15, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Lugaha ku riix marka hore, dhabarka gadaal u leexi, gacmaha xagga caloosha u soo jiid."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Stair Climber",
        "target_muscle": "Glutes & Quads & Extreme Cardio",
        "description": "Mashiinka jaranjarada ee qaabeeya badhida iyo lugaha.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=stair%20master%203d",
        "default_duration": 15, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Jaranjarada fuul adoo cagta oo dhan saaraya, toos u istaag adoon gacmaha ku tiirsanayn."
    },
    {
        "category": "Cardio", "subcategory": "Cardio", "name": "Elliptical",
        "target_muscle": "Low-Impact Full Body Cardio",
        "description": "Mashiinka wareegga ee aan culeys saarayn jilbaha.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=elliptical%20exercise%203d",
        "default_duration": 20, "default_sets": 1, "default_reps": 1,
        "correct_form_instructions": "Gacmaha iyo lugaha isku mar dhaqaaji adoo dhabarka toosinaya."
    },
]


class Command(BaseCommand):
    help = "Populate ExerciseLibrary with complete ~80 exercises organized by category and subcategory using update_or_create"

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            dest='skip_if_exists',
            help='Skip seeding if exercises already exist in the database',
        )

    def handle(self, *args, **options):
        if options.get('skip_if_exists') and ExerciseLibrary.objects.exists():
            self.stdout.write(self.style.SUCCESS(f'Exercises already exist ({ExerciseLibrary.objects.count()} records). Skipping seed.'))
            return
        updated_or_created = 0
        for item in EXERCISES_DATA:
            obj, created = ExerciseLibrary.objects.update_or_create(
                category=item["category"],
                subcategory=item["subcategory"],
                name=item["name"],
                defaults={
                    "target_muscle": item.get("target_muscle", ""),
                    "description": item.get("description", ""),
                    "image_url": item.get("image_url", ""),
                    "video_3d_url": item.get("video_3d_url", ""),
                    "correct_form_instructions": item.get("correct_form_instructions", ""),
                    "default_duration": item.get("default_duration", 15),
                    "default_sets": item.get("default_sets", 4),
                    "default_reps": item.get("default_reps", 10),
                }
            )
            updated_or_created += 1

        total_count = ExerciseLibrary.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Successfully processed {updated_or_created} exercises. Total in library: {total_count}"))
