import logging

from django.core.management.base import NoArgsCommand

log = logging.getLogger( 'regenerate_widgets' )

class Command(NoArgsCommand):
    help = 'regenerate rendered_widgets of all pages'

    def handle(self, *args, **options):
        import sys
        from mypage.widgets.models import RenderedWidget

        error_count = 0
        # process individual RenderedWidget objects
        for rw in RenderedWidget.objects.all():
            try:
                rw.save()
            except Exception, e:
                log.error(u'Regenerating widget failed for rendered widget %d (%r).', rw.pk, e)
                error_count += 1

        sys.exit(error_count)

