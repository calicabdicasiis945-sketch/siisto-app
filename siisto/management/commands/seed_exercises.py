from django.core.management.base import BaseCommand
from siisto.models import ExerciseLibrary

EXERCISES_DATA = [
    # ==================== CHEST ====================
    {
        "category": "Chest", "subcategory": "Compound", "name": "Bench Press",
        "target_muscle": "Mid & Overall Pectorals (Xabadka Guud)",
        "description": "Jimicsiga ugu caansan ee dhisidda xabadka buuxa iyo awoodda riixitaanka.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/pin/bench-press-3d-exercise-animation--123456789/",
        "default_duration": 15, "default_sets": 4, "default_reps": 10
    },
    {
        "category": "Chest", "subcategory": "Upper Chest", "name": "Incline Bench Press",
        "target_muscle": "Clavicular Upper Chest (Xabadka Sare)",
        "description": "Kordhinta dhumucda iyo buuxnaanta xabadka sare.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=incline%20bench%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10
    },
    {
        "category": "Chest", "subcategory": "Lower Chest", "name": "Decline Bench Press",
        "target_muscle": "Lower Pectorals (Xabadka Hoose)",
        "description": "Dhisidda iyo qeexidda xariiqda hoose ee muruqa xabadka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=decline%20bench%20press%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Chest", "subcategory": "Dumbbell", "name": "Dumbbell Press",
        "target_muscle": "Chest Stretch & Stabilization",
        "description": "Riixitaanka dumbbells-ka oo siinaya xabadka dhaqdhaqaaq qoto dheer.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20chest%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10
    },
    {
        "category": "Chest", "subcategory": "Isolation", "name": "Dumbbell Fly",
        "target_muscle": "Pectoral Stretch & Expansion",
        "description": "Kala bixidda xabadka oo ballaarisa qafiska feeraha.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20fly%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Chest", "subcategory": "Cable", "name": "Cable Fly",
        "target_muscle": "Inner Chest & Squeeze Contraction",
        "description": "Qanjiirka xabadka dhexdiisa oo adkeeya muruqa xabadka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20fly%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Chest", "subcategory": "Bodyweight", "name": "Push Up",
        "target_muscle": "Chest, Front Delts & Core",
        "description": "Jimicsiga asalka ah ee miisaanka jirka lagu riixo ee xabadka.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=push%20up%203d%20animation",
        "default_duration": 10, "default_sets": 4, "default_reps": 15
    },
    {
        "category": "Chest", "subcategory": "Bodyweight", "name": "Chest Dip",
        "target_muscle": "Lower Chest & Triceps",
        "description": "Hoos u daadashada iyo kor u riixitaanka birta ee xabadka hoose.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=chest%20dips%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },

    # ==================== BACK ====================
    {
        "category": "Back", "subcategory": "Bodyweight", "name": "Pull Up",
        "target_muscle": "Latissimus Dorsi (Lats) & Upper Back",
        "description": "Isku qaadista birta ee ballaarisa dhabarka sare.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=pull%20up%203d%20exercise",
        "default_duration": 12, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Back", "subcategory": "Bodyweight", "name": "Chin Up",
        "target_muscle": "Lats & Biceps",
        "description": "Isku qaadista birta ee calaacalaha soo jeedaan oo dhabarka iyo gacanta dhista.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=chin%20up%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },
    {
        "category": "Back", "subcategory": "Cable", "name": "Lat Pulldown",
        "target_muscle": "Lats Width (Ballaarinta Dhabarka)",
        "description": "Hoos u soo jiididda birta ballaaran ee dhabarka sare.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lat%20pulldown%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 10
    },
    {
        "category": "Back", "subcategory": "Free Weight", "name": "Barbell Row",
        "target_muscle": "Mid Back & Rhomboids (Dhumucda Dhabarka)",
        "description": "Soo jiididda barbalka culus adoo foorara oo dhabarka dhumuc weyn siiya.",
        "image_url": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20row%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Back", "subcategory": "Dumbbell", "name": "Dumbbell Row",
        "target_muscle": "Single-Arm Lat Focus",
        "description": "Dhabar jiidista dumbbell hal-hal gacan ah oo isu dheellitirta murqaha.",
        "image_url": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20row%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10
    },
    {
        "category": "Back", "subcategory": "Cable", "name": "Seated Cable Row",
        "target_muscle": "Mid Back & Traps",
        "description": "Fadhi ku soo jiididda cable-ka oo dhabarka dhexdiisa adkeyneysa.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=seated%20cable%20row%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Back", "subcategory": "Machine", "name": "T-Bar Row",
        "target_muscle": "Deep Back Thickness",
        "description": "Jiidista T-Bar-ka culus oo dhabarka siinaysa awood iyo qaab dhumuc weyn.",
        "image_url": "https://images.unsplash.com/photo-1605296867304-46d5465a13f1?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=t%20bar%20row%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Back", "subcategory": "Compound", "name": "Deadlift",
        "target_muscle": "Full Posterior Chain & Spine",
        "description": "Boqorka jimicsiyada ee dhisidda dhabarka hoose, badhida iyo muruqa guud.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=deadlift%203d%20exercise",
        "default_duration": 20, "default_sets": 4, "default_reps": 6
    },
    {
        "category": "Back", "subcategory": "Isolation", "name": "Straight Arm Pulldown",
        "target_muscle": "Lat Isolation & Serratus",
        "description": "Hoos u riixitaanka gacmaha toosan ee cable-ka oo go'doominaya lats-ka.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=straight%20arm%20pulldown%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },

    # ==================== SHOULDERS ====================
    # Front Delts
    {
        "category": "Shoulders", "subcategory": "Front Delts", "name": "Front Raise",
        "target_muscle": "Anterior Deltoid (Garabka Hore)",
        "description": "Kor u qaadista miisaanka ee garabka hore.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=front%20raise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Shoulders", "subcategory": "Front Delts", "name": "Arnold Press",
        "target_muscle": "Rotational Front & Side Delts",
        "description": "Wareejinta dumbbells-ka inta la riixayo ee garabka buuxa dhisa.",
        "image_url": "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=arnold%20press%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10
    },
    # Side Delts
    {
        "category": "Shoulders", "subcategory": "Side Delts", "name": "Lateral Raise",
        "target_muscle": "Lateral Deltoid (Ballaarinta Garabka)",
        "description": "Dhinac u qaadista dumbbells-ka ee garabka ballaadhisa.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lateral%20raise%203d",
        "default_duration": 10, "default_sets": 4, "default_reps": 15
    },
    {
        "category": "Shoulders", "subcategory": "Side Delts", "name": "Upright Row",
        "target_muscle": "Side Delts & Traps",
        "description": "Kor u soo jiididda miisaanka ilaa laabta.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=upright%20row%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    # Rear Delts
    {
        "category": "Shoulders", "subcategory": "Rear Delts", "name": "Rear Delt Fly",
        "target_muscle": "Posterior Deltoid (Garabka Dambe)",
        "description": "Kala bixidda garabka dambe ee dhabarka sare.",
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=rear%20delt%20fly%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Shoulders", "subcategory": "Rear Delts", "name": "Face Pull",
        "target_muscle": "Rear Delts & Rotator Cuff",
        "description": "Jiidista xadhigga cable-ka xagga wejiga oo garabka caafimaadkiisa dhisa.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=face%20pull%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Shoulders", "subcategory": "Rear Delts", "name": "Reverse Pec Deck",
        "target_muscle": "Rear Delts Machine Isolation",
        "description": "Mashiinka dhabar riixista ee garabka dambe.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20pec%20deck%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    # Compound Shoulders
    {
        "category": "Shoulders", "subcategory": "Compound", "name": "Overhead Press",
        "target_muscle": "Full Shoulder Girdle & Triceps",
        "description": "Kor u riixitaanka barbalka toosan adoo taagan.",
        "image_url": "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=overhead%20press%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Shoulders", "subcategory": "Compound", "name": "Dumbbell Shoulder Press",
        "target_muscle": "Shoulders Mass Builder",
        "description": "Riixitaanka dumbbells-ka sare ee garabka.",
        "image_url": "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20shoulder%20press%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10
    },
    {
        "category": "Shoulders", "subcategory": "Compound", "name": "Machine Shoulder Press",
        "target_muscle": "Shoulders Hypertrophy Machine",
        "description": "Riixitaanka mashiinka garabka oo badbaado sare leh.",
        "image_url": "https://images.unsplash.com/photo-1532029837206-abbe2b7620e3?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=machine%20shoulder%20press%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },

    # ==================== ARMS ====================
    # Biceps
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Barbell Curl",
        "target_muscle": "Biceps Overall Mass",
        "description": "Laalaabista barbalka ee dhisidda gacanta hore.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Dumbbell Curl",
        "target_muscle": "Biceps Isolation",
        "description": "Dumbbell curl hal-hal gacan ah oo gacanta joog sare siisa.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dumbbell%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Hammer Curl",
        "target_muscle": "Brachialis & Forearm Thickness",
        "description": "Gacanta oo toosan inta la laalaabayo dumbbell-ka (Hammer style).",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=hammer%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Concentration Curl",
        "target_muscle": "Biceps Peak",
        "description": "Fadhi ku go'doominta muruqa biceps-ka.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=concentration%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Preacher Curl",
        "target_muscle": "Biceps Short Head",
        "description": "Koorso ku tiirinta gacmaha ee preacher bench.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=preacher%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },
    {
        "category": "Arms", "subcategory": "Biceps", "name": "Cable Curl",
        "target_muscle": "Constant Tension Biceps",
        "description": "Laalaabista cable-ka oo culeyska joogto ka dhigaya.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    # Triceps
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Tricep Pushdown",
        "target_muscle": "Triceps Lateral Head",
        "description": "Hoos u riixitaanka birta toosan ee cable-ka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=tricep%20pushdown%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Overhead Extension",
        "target_muscle": "Triceps Long Head (Buuxinta Gacanta Dambe)",
        "description": "Madaxa dushiisa ka riixitaanka dumbbell-ka.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=tricep%20overhead%20extension%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Skull Crusher",
        "target_muscle": "Triceps Long & Medial Head",
        "description": "Jiif ku laalaabista barbalka xagga madaxa.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=skull%20crusher%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Close Grip Bench Press",
        "target_muscle": "Triceps Compound Power",
        "description": "Xabad riixista qabsashada dhow ee triceps-ka dhista.",
        "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=close%20grip%20bench%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Bench Dips",
        "target_muscle": "Bodyweight Triceps",
        "description": "Kursiga gadaashiisa ka degidda ee gacanta dambe.",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=bench%20dips%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Arms", "subcategory": "Triceps", "name": "Rope Pushdown",
        "target_muscle": "Triceps Peak & Separation",
        "description": "Riixitaanka xadhigga cable-ka ee kala bixiya gacanta dambe.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=rope%20tricep%20pushdown%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    # Forearms
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Wrist Curl",
        "target_muscle": "Forearm Flexors (Cumaacada Hore)",
        "description": "Laalaabista cumaacada ee curcurka gacanta.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=wrist%20curl%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Reverse Wrist Curl",
        "target_muscle": "Forearm Extensors",
        "description": "Kor u qaadista cumaacada dhabarkeeda.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20wrist%20curl%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Farmer's Walk",
        "target_muscle": "Grip Strength & Forearms & Traps",
        "description": "Socodka adoo labada gacmood culeys culus ku haya.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=farmers%20walk%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 1
    },
    {
        "category": "Arms", "subcategory": "Forearms", "name": "Reverse Curl",
        "target_muscle": "Brachioradialis & Forearms",
        "description": "Laalaabista barbalka adoo calaacalaha hoos u jeediyay.",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },

    # ==================== LEGS ====================
    # Quadriceps
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Squat",
        "target_muscle": "Quadriceps & Full Leg Mass",
        "description": "Boqorka jimicsiyada lugaha ee dhisidda bowdada.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20squat%203d",
        "default_duration": 18, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Front Squat",
        "target_muscle": "Quad Dominant Squat",
        "description": "Koorso ku qaadista barbalka xabadka hore.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=front%20squat%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 8
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Leg Press",
        "target_muscle": "Heavy Quad Overload",
        "description": "Riixitaanka mashiinka lugaha ee bowdada.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=leg%20press%203d",
        "default_duration": 12, "default_sets": 4, "default_reps": 12
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Leg Extension",
        "target_muscle": "Quad Isolation & Tear-drop Muscle",
        "description": "Fadhi ku toosinta lugaha ee mashiinka.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=leg%20extension%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Legs", "subcategory": "Quadriceps", "name": "Bulgarian Split Squat",
        "target_muscle": "Single Leg Quads & Glutes",
        "description": "Hal lug dib u saarista kursiga ee dhisidda bowdooyinka goonida ah.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=bulgarian%20split%20squat%203d",
        "default_duration": 12, "default_sets": 3, "default_reps": 10
    },
    # Hamstrings
    {
        "category": "Legs", "subcategory": "Hamstrings", "name": "Romanian Deadlift",
        "target_muscle": "Hamstrings Stretch & Glutes",
        "description": "Foorarsiga barbalka adoo lugaha toosan ku haysta ee bowdada dambe.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=romanian%20deadlift%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 10
    },
    {
        "category": "Legs", "subcategory": "Hamstrings", "name": "Leg Curl",
        "target_muscle": "Hamstrings Isolation",
        "description": "Jiif ama fadhi ku laalaabista bowdada dambe.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lying%20leg%20curl%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Legs", "subcategory": "Hamstrings", "name": "Good Morning",
        "target_muscle": "Hamstrings & Lower Back",
        "description": "Garabka saarista barbalka iyo foorarsiga.",
        "image_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=good%20morning%20exercise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },
    # Glutes
    {
        "category": "Legs", "subcategory": "Glutes", "name": "Hip Thrust",
        "target_muscle": "Gluteus Maximus",
        "description": "Kor u qaadista miskaha adoo kursiga dhabarka ku haya.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=barbell%20hip%20thrust%203d",
        "default_duration": 15, "default_sets": 4, "default_reps": 10
    },
    {
        "category": "Legs", "subcategory": "Glutes", "name": "Glute Bridge",
        "target_muscle": "Glutes & Hamstrings",
        "description": "Dhulka jiifka ku qaadista miskaha.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=glute%20bridge%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Legs", "subcategory": "Glutes", "name": "Cable Kickback",
        "target_muscle": "Glute Isolation",
        "description": "Dhabar u laadista lugta ee cable-ka.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20kickback%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    # Calves
    {
        "category": "Legs", "subcategory": "Calves", "name": "Standing Calf Raise",
        "target_muscle": "Gastrocnemius (Kubka Taagan)",
        "description": "Faraha lugaha ku joogsiga ee dhisidda kubka.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=standing%20calf%20raise%203d",
        "default_duration": 8, "default_sets": 4, "default_reps": 15
    },
    {
        "category": "Legs", "subcategory": "Calves", "name": "Seated Calf Raise",
        "target_muscle": "Soleus (Kubka Fadhiga)",
        "description": "Fadhi ku qaadista culeyska faraha lugaha.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=seated%20calf%20raise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Legs", "subcategory": "Calves", "name": "Donkey Calf Raise",
        "target_muscle": "Full Calf Stretch",
        "description": "Foorarsi ku qaadista kubka oo siinaya fiditaan buuxa.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=donkey%20calf%20raise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },

    # ==================== ABS / CORE ====================
    # Upper Abs
    {
        "category": "Abs / Core", "subcategory": "Upper Abs", "name": "Crunch",
        "target_muscle": "Upper Rectus Abdominis (Caloosha Sare)",
        "description": "Kalaabista caloosha sare ee dhulka.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=crunch%203d%20exercise",
        "default_duration": 8, "default_sets": 3, "default_reps": 20
    },
    {
        "category": "Abs / Core", "subcategory": "Upper Abs", "name": "Cable Crunch",
        "target_muscle": "Weighted Upper Abs",
        "description": "Jilbaha ku fadhiga iyo hoos u soo jiidista xadhigga caloosha.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cable%20crunch%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Abs / Core", "subcategory": "Upper Abs", "name": "Sit Up",
        "target_muscle": "Full Abdominal Wall",
        "description": "Fadhiga buuxa ee caloosha.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=sit%20up%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },
    # Lower Abs
    {
        "category": "Abs / Core", "subcategory": "Lower Abs", "name": "Leg Raise",
        "target_muscle": "Lower Abs (Caloosha Hoose)",
        "description": "Jiif ku qaadista labada lugood.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=lying%20leg%20raise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },
    {
        "category": "Abs / Core", "subcategory": "Lower Abs", "name": "Hanging Leg Raise",
        "target_muscle": "Lower Abs & Hip Flexors",
        "description": "Birta sudhnaanta ku qaadista lugaha.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=hanging%20leg%20raise%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Abs / Core", "subcategory": "Lower Abs", "name": "Reverse Crunch",
        "target_muscle": "Lower Abdominals",
        "description": "Miskaha xagga xabadka u soo laalaabida.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=reverse%20crunch%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 15
    },
    # Obliques
    {
        "category": "Abs / Core", "subcategory": "Obliques", "name": "Russian Twist",
        "target_muscle": "Obliques (Dhinacyada Caloosha)",
        "description": "Wareejinta dhinacyada caloosha adoo culeys haya.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=russian%20twist%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 20
    },
    {
        "category": "Abs / Core", "subcategory": "Obliques", "name": "Side Plank",
        "target_muscle": "Side Core Stability",
        "description": "Dhinac ku joogsiga plank-ga.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=side%20plank%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 45
    },
    {
        "category": "Abs / Core", "subcategory": "Obliques", "name": "Bicycle Crunch",
        "target_muscle": "Rotational Abs",
        "description": "Baaskiil ku samaynta caloosha ee jiifka ah.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=bicycle%20crunch%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 20
    },
    # Core
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Plank",
        "target_muscle": "Isometric Full Core",
        "description": "Dhisidda adkeysiga buuxa ee caloosha iyo dhabarka.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=plank%203d%20exercise",
        "default_duration": 5, "default_sets": 3, "default_reps": 60
    },
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Mountain Climber",
        "target_muscle": "Dynamic Core & Cardio",
        "description": "Orodka jilbaha adoo plank ku jira.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=mountain%20climber%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 30
    },
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Dead Bug",
        "target_muscle": "Deep Core Stability",
        "description": "Isu celinta gacanta iyo lugta ee dhabarka jiifka.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=dead%20bug%20exercise%203d",
        "default_duration": 8, "default_sets": 3, "default_reps": 12
    },
    {
        "category": "Abs / Core", "subcategory": "Core", "name": "Ab Wheel Rollout",
        "target_muscle": "Advanced Core Stretch",
        "description": "Taayirka caloosha lagu rogo ee adkeynta buuxda.",
        "image_url": "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=ab%20wheel%20rollout%203d",
        "default_duration": 10, "default_sets": 3, "default_reps": 10
    },

    # ==================== CARDIO ====================
    {
        "category": "Cardio", "subcategory": "General", "name": "Walking",
        "target_muscle": "Low-Impact Calorie Burn (Socod)",
        "description": "Socodka caadiga ah ee gubidda baruurta iyo caafimaadka wadnaha.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=brisk%20walking%20exercise",
        "default_duration": 30, "default_sets": 1, "default_reps": 1
    },
    {
        "category": "Cardio", "subcategory": "General", "name": "Running",
        "target_muscle": "High Calorie Burn (Orod)",
        "description": "Orodka degdegga ah ee adkeynta wadnaha iyo sambabada.",
        "image_url": "https://images.unsplash.com/photo-1530549387789-4c1017266635?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=running%20exercise%203d",
        "default_duration": 20, "default_sets": 1, "default_reps": 1
    },
    {
        "category": "Cardio", "subcategory": "Machine", "name": "Treadmill",
        "target_muscle": "Cardiovascular Conditioning",
        "description": "Mashiinka orodka iyo socodka ee qolka jimicsiga.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=treadmill%20running%203d",
        "default_duration": 25, "default_sets": 1, "default_reps": 1
    },
    {
        "category": "Cardio", "subcategory": "General", "name": "Cycling",
        "target_muscle": "Leg Endurance & Cardio (Baaskiil)",
        "description": "Wadida baaskiilka ee kordhisa adkeysiga lugaha.",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=cycling%20exercise%203d",
        "default_duration": 25, "default_sets": 1, "default_reps": 1
    },
    {
        "category": "Cardio", "subcategory": "General", "name": "Jump Rope",
        "target_muscle": "Agility & Calf & Fat Loss (Xadhig Bood)",
        "description": "Xadhig boodka degdegga ah ee guba baruurta badan.",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=jump%20rope%203d%20animation",
        "default_duration": 15, "default_sets": 3, "default_reps": 100
    },
    {
        "category": "Cardio", "subcategory": "Machine", "name": "Rowing Machine",
        "target_muscle": "Full Body Cardio & Back",
        "description": "Mashiinka doon-wadida ee tababara 85% murqaha jirka.",
        "image_url": "https://images.unsplash.com/photo-1521804906057-1df8fdb718b7?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=rowing%20machine%203d",
        "default_duration": 15, "default_sets": 1, "default_reps": 1
    },
    {
        "category": "Cardio", "subcategory": "Machine", "name": "Stair Climber",
        "target_muscle": "Glutes & Quads & Extreme Cardio",
        "description": "Mashiinka jaranjarada ee qaabeeya badhida iyo lugaha.",
        "image_url": "https://images.unsplash.com/photo-1434682881908-b43d0467b798?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=stair%20master%203d",
        "default_duration": 15, "default_sets": 1, "default_reps": 1
    },
    {
        "category": "Cardio", "subcategory": "Machine", "name": "Elliptical",
        "target_muscle": "Low-Impact Full Body Cardio",
        "description": "Mashiinka wareegga ee aan culeys saarayn jilbaha.",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?q=80&w=600&auto=format&fit=crop",
        "video_3d_url": "https://www.pinterest.com/search/pins/?q=elliptical%20exercise%203d",
        "default_duration": 20, "default_sets": 1, "default_reps": 1
    },
]


class Command(BaseCommand):
    help = "Populate exact categorized exercise library with 3D video links"

    def handle(self, *args, **options):
        # Clear previous exercises and replace with the exact required list
        ExerciseLibrary.objects.all().delete()
        created_count = 0
        for item in EXERCISES_DATA:
            ExerciseLibrary.objects.create(
                name=item["name"],
                category=item["category"],
                subcategory=item["subcategory"],
                target_muscle=item["target_muscle"],
                description=item["description"],
                image_url=item["image_url"],
                video_3d_url=item["video_3d_url"],
                default_duration=item["default_duration"],
                default_sets=item["default_sets"],
                default_reps=item["default_reps"],
            )
            created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} exercises into database!"))
