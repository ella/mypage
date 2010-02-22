from mypage.widgets.management.commands import LockedCommand
from mypage.widgets.conf import settings


class Command(LockedCommand):
    help = 'Fetch all registered imports in cronjob.'
    cachelock = settings.MYPAGE_FETCH_CACHELOCK
    pid_file = settings.MYPAGE_FETCH_PIDFILE

    def logic(self, *args, **options):
        from mypage.widgets.management.commands import fetch_widgets
        self.errors = fetch_widgets.Command().handle(*args, **options)

    def out(self):
        import sys
        sys.exit(self.errors)

