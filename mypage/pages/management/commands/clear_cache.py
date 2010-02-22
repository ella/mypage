from django.core.management.base import NoArgsCommand

from mypage.pages.models import skin_choices

class Command(NoArgsCommand):
    help = 'clear pages and widgets from cache'

    def handle(self, *args, **options):
        from django.core.cache import cache
        from django.conf import settings

        from mypage.widgets.models import Widget, get_widget_cache_key, get_content_cache_key
        from mypage.pages.views import RENDERED_PAGE_KEY

        for w in Widget.objects.all():
            cache.delete(get_widget_cache_key(widget=w))
            cache.delete(get_content_cache_key(widget=w))

        for show_welcome in (2, 3):
            for skin, x in skin_choices() + (("-", "default"),):
                cache.delete(RENDERED_PAGE_KEY % {
                     "pk": settings.DEFAULT_PAGE_ID, 
                     "show_welcome": show_welcome,
                     "skin" : skin,
                 })
