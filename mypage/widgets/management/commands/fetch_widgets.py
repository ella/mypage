import logging
import threading
from Queue import Queue, Empty
import datetime
import socket

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.core.cache import cache

from mypage.widgets.models import Widget

log = logging.getLogger('mypage.widgets.fetch_widgets')

fetching = False
error_count = 0

def fetch(queue):
    global error_count
    while not queue.empty() or fetching:
        try:
            w = queue.get(True, 1)
            log.info(u'Fetch started for %s.', w.pk)
            w.fetch_data()
            log.info(u'Fetch ended for %s.', w.pk)

        except Empty:
            # nothing waiting for us in the queue
            pass

        except Exception, e:
            log.warning(u'Fetching for %s failed (%r).', w.pk, e)
            # ideally, we should lock during accessing error_count, but since it's sole
            # purpose is to identify IF an error has occured, we don't care
            error_count += 1

class Command(NoArgsCommand):
    help = 'Fetch all registered imports'

    def handle(self, *test_labels, **options):
        """
        TODO:
        until some clever cron or external queue is used
        there is simple cache lock mechanism
        """
        global fetching, error_count

        # if verbosity set enforce it in global logger or disable
        verbosity = options.get('verbosity')
        if verbosity >= 1:
            log.setLevel(logging.INFO)
        else:
            log.setLevel(logging.WARNING)

        now = datetime.datetime.now()

        fetching = True
        error_count = 0

        # fetch queue
        queue = Queue(100)

        # initiate consumer threads
        threads = [threading.Thread(None, fetch, args=(queue,)) for a in range(getattr(settings, 'FETCHWIDGET_THREADS', 2))]

        # fire up the threads
        for thread in threads:
            thread.start()

        # set timeout for outgoing connection so that we do not hang
        # TODO: add config value to settings?
        socket.setdefaulttimeout(10)

        # process individual Widget objects
        for w in Widget.objects.filter(next_download__lte=now).order_by('next_download'):
            # TODO: put some external queue here for future scaling-up
            # fetch() would then become something consuming that queue
            queue.put(w.get_child())

        # end of processing
        fetching = False

        # collect all threads
        for thread in threads:
            while thread.isAlive():
                thread.join( 1 )

        return error_count

