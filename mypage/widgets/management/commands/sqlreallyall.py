from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = 'print output of sqlall for each installed app'

    def handle(self, *args, **options):
        from django.core.management import call_command
        from django.conf import settings

        for a in settings.INSTALLED_APPS:
            app = a.split('.')[-1]
            call_command('sqlall', app)

