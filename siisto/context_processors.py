from django.conf import settings
from django.utils import translation

LANGUAGE_SESSION_KEY = getattr(translation, 'LANGUAGE_SESSION_KEY', '_language')


def siisto_i18n(request):
    """
    Context processor providing active language, RTL status, and language choices.
    """
    lang = None
    if hasattr(request, 'session') and LANGUAGE_SESSION_KEY in request.session:
        lang = request.session[LANGUAGE_SESSION_KEY]
    elif hasattr(request, 'COOKIES') and getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language') in request.COOKIES:
        lang = request.COOKIES[getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')]
    elif hasattr(request, 'user') and request.user.is_authenticated:
        try:
            lang = request.user.profile.preferred_language
        except Exception:
            pass

    if not lang:
        lang = translation.get_language() or getattr(settings, 'LANGUAGE_CODE', 'so') or 'so'

    lang = str(lang)[:2].lower()
    if lang not in ['so', 'en', 'ar']:
        lang = 'so'

    is_rtl = (lang == 'ar')

    languages = [
        {'code': 'so', 'name': 'Soomaali', 'flag': '🇸🇴', 'is_active': (lang == 'so')},
        {'code': 'en', 'name': 'English', 'flag': '🇬🇧', 'is_active': (lang == 'en')},
        {'code': 'ar', 'name': 'العربية', 'flag': '🇸🇦', 'is_active': (lang == 'ar')},
    ]

    return {
        'CURRENT_LANGUAGE': lang,
        'IS_RTL': is_rtl,
        'ACTIVE_LANG_DIR': 'rtl' if is_rtl else 'ltr',
        'AVAILABLE_LANGUAGES': languages,
    }
