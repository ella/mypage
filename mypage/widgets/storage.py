from django.core.cache import get_cache
from django.conf import settings

storage = get_cache(settings.MYPAGE_STORAGE_BACKEND)

