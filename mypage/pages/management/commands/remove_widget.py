import time
from optparse import make_option

from django.core.management.base import CommandError, BaseCommand

from mypage.widgets.models import Widget
from mypage.pages.models import Page

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--loop-sleep', default=0.001, dest='loop_sleep', type='float',
            help='Specifies time sleep (in seconds) between every page update.'),
    )
    help = 'Remove a widget from all pages and its layouts'
    args = 'widget_pk'

    def handle(self, widget_pk, **options):

        loop_sleep = options.get('loop_sleep', 0.001)

        widget = Widget.objects.get(pk=widget_pk)

        for p in Page.objects.all().iterator():
            p.remove_widget(widget)
            time.sleep(loop_sleep)
