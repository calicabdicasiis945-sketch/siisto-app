from django.conf import settings
from django.utils import translation

def siisto_i18n(request):
    """
    Context processor providing active language, RTL status, and language choices.
    """
    lang = translation.get_language() or settings.LANGUAGE_CODE or 'so'
    
    # If user is authenticated and has a preferred language, sync if needed
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            user_lang = request.user.profile.preferred_language
            if user_lang and user_lang != lang:
                # If session has no override yet, respect profile
                if translation.LANGUAGE_SESSION_KEY not in request.session:
                    lang = user_lang
                    translation.activate(lang)
                    request.session[translation.LANGUAGE_SESSION_KEY] = lang
        except Exception:
            pass

    is_rtl = lang.startswith('ar')
    
    languages = [
        {'code': 'so', 'name': 'Soomaali', 'flag': '🇸🇴', 'is_active': lang.startswith('so')},
        {'code': 'en', 'name': 'English', 'flag': '🇬🇧', 'is_active': lang.startswith('en')},
        {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦', 'is_active': lang.startswith('ar')},
    ]

    return {
        'CURRENT_LANGUAGE': lang,
        'IS_RTL': is_rtl,
        'ACTIVE_LANG_DIR': 'rtl' if is_rtl else 'ltr',
        'AVAILABLE_LANGUAGES': languages,
    }
