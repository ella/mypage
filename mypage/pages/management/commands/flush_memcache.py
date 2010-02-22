from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = 'if cache backend is set to memcachd invalidate all data, try to do it for other backends as well'

    def handle(self, *args, **options):
        from django.conf import settings
        from django.core.cache import cache

        backend = settings.CACHE_BACKEND.split('://')[0]

        if backend == 'memcached':
            cache._cache.flush_all()
        elif backend == 'locmem':
            cache._cache = {}
            cache._expire_info = {}

