from optparse import make_option

from django.core.management.base import CommandError, BaseCommand
from django.db.models.query import QuerySet

from mypage.pages.migrations.utils.layout_refactor_migration import migrate
from mypage.pages.models import Page

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--limit', default=None, dest='limit', type='int',
            help='Number of pages to be migrated.'),
        make_option('--loop-sleep', default=0.001, dest='loop_sleep', type='float',
            help='Specifies time sleep (in seconds) between every page update.'),
        make_option('--info', action='store_true', default=False, dest='info',
            help='Prints non/migrated pages count.'),
    )
    help = 'Migrates refactored page layouts'

    def handle(self, **options):

        limit = options.get('limit',None)
        loop_sleep = options.get('loop_sleep', 0.001)
        info = options.get('info', False)

        if info:
            qs = QuerySet(model=Page)
            nonmigrated = qs.filter(layout_migrated=False).count()
            total = qs.count()
            l = len(str(total))
            print str(total-nonmigrated).rjust(l), 'pages allready migrated'
            print str(nonmigrated).rjust(l), 'pages NOT YET migrated'
            print str(total).rjust(l), "pages TOTAL"
            return

        migrate(limit, loop_sleep)


