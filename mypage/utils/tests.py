import itertools

from django.core.cache import cache
from django.core.management import call_command
from django.core.exceptions import ImproperlyConfigured

from mypage.widgets.models import Widget, get_data_cache_key, get_object
from mypage.widgets.storage import storage
from mypage import pages
import mypage.pages.models
import mypage.pages.managers


def clear_widgets_data_cache():
    "clear widgets' data in cache"
    for w in Widget.objects.all():
        ck = get_data_cache_key(widget=w)
        storage.delete(ck)

def get_data_from_cache():
    "verify data in cache"
    widgets_with_data = []
    for w in Widget.objects.all():
        ck = get_data_cache_key(widget=w)
        data = storage.get(ck)
        if data: widgets_with_data.append(w)
    return widgets_with_data

def flushdb_loaddata(*fixtures):
    call_command('resetmypagedb', verbosity=0, interactive=False)
    call_command('flush_memcache', verbosity=0, interactive=False)

    for f in fixtures:
        call_command('loaddata', f, verbosity=False)

    try:
        call_command('regenerate_widgets', verbosity=0, interactive=False)
    except SystemExit:
        pass

def print_layout(page):
    for c in ('containers', 'static_containers'):
        for i,j in enumerate(page.layout[c]):
            print '%s-%d' % (c, i), [repr(get_object(*k)) for k in j]

def get_layout_list(page):
    layout_list = sorted( [ i for i in map(lambda x: (int(x[0]), int(x[1])), itertools.chain(* page.layout['containers'] + page.layout['static_containers'])) ] )
    return layout_list

def get_wips_list(page):
    wips = page.widgetinpage_set.select_related('widget')
    wips_list = sorted( [ (int(wip.widget.content_type_id), int(wip.widget.pk)) for wip in wips ] )
    return wips_list

