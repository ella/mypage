from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = 'load some contenttypes from fixtures and after that call syncdb'

    def handle(self, *args, **options):
        from django.core.management import call_command

        call_command('loaddata', 'frozen_contenttypes', verbosity=False)
        call_command('syncdb', verbosity=False)

