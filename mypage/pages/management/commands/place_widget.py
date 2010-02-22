import time
import logging
from optparse import make_option

from django.core.management.base import CommandError, BaseCommand
from django.db import transaction

from mypage.widgets.models import Widget
from mypage.pages.models import Page

log = logging.getLogger('mypage.pages.place_widget')

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--container', default=0, dest='container', type='int',
            help='Specifies the layout container where to place the widget.'),
        make_option('--position', default=None, dest='position', type='int',
            help='Specifies the layout container position where to place the widget.'),
        make_option('--loop-sleep', default=0.001, dest='loop_sleep', type='float',
            help='Specifies time sleep (in seconds) between every page update.'),
        make_option('--delete-broken-pages', action='store_true', default=False, dest='delete_broken_pages',
            help='Pages with broken layout will be deleted.'),
    )
    help = 'Adds a widget to all pages and place it into their layouts'
    args = 'widget_pk'

    def handle(self, widget_pk, **options):

        widget = Widget.objects.get(pk=widget_pk)

        container = options.get('container',0)
        position = options.get('position',None)
        loop_sleep = options.get('loop_sleep', 0.001)
        delete_broken_pages = options.get('delete_broken_pages')

        for p in Page.objects.exclude(widgetinpage__widget=widget).iterator():
            placed = self.place_widget(p, widget, container=container, position=position)
            #if not placed:
            #    #behave = 'Page update skipped.'
            #    #if delete_broken_pages:
            #    #    p.delete()
            #        #behave = 'Page deleted.'
            #    #log.warning(u'Cannot add widget to page pk=%d (%s). %s', p.pk, e, behave)
            time.sleep(loop_sleep)

    @transaction.commit_manually
    def place_widget(self, page, widget, container, position):
        try:
            page.add_widget(widget, container=container, position=position)
        except Exception, e:
            # FIXME add_widget and Layout should throw their own exceptions
            # list index out of range (containers) - to few containers
            # no JSON code could be decoded - BrokenLayoutError
            transaction.rollback()
            log.warning(u'Cannot add widget to page pk=%d (%s)', page.pk, e)
            return False
        else:
            transaction.commit()
            return True
