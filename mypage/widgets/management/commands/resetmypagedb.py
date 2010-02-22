from django.core.management.base import BaseCommand

from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-e', '--exclude', dest='exclude',action='append', default=[],
            help='App to exclude from reset (use multiple --exclude to exclude multiple apps).'),
    )
    help = 'Reset database and load frozen contentypes and syncdb'

    def handle(self, *args, **options):
        from django.core.management import call_command
        from django.conf import settings

        exclude = options.get('exclude',[])

        for a in settings.INSTALLED_APPS:
            app = a.split('.')[-1]
            if app not in exclude:
                call_command('reset', app, verbosity=False, interactive=False)

        call_command('loaddata', 'frozen_contenttypes', verbosity=False)
        call_command('syncdb', verbosity=False)

