from django.core.management.base import NoArgsCommand
from mypage.widgets.conf import settings


class LockedCommand(NoArgsCommand):
    help = 'helper command that locks iteslf and kills predecessors'
    cachelock = settings.MYPAGE_COMMAND_CACHELOCK
    cachelock_timeout = settings.MYPAGE_COMMAND_CACHELOCK_TIMEOUT
    pid_file = settings.MYPAGE_COMMAND_PIDFILE

    def logic(self, *args, **options):
        pass

    def out(self):
        pass

    def handle(self, *args, **options):
        """
        TODO:
        until some clever cron or external queue is used
        there is simple cache lock mechanism
        """
        from os import getpid, kill, path, remove
        import time
        from mypage.widgets.storage import storage

        if self.cachelock is not None:
            # cache lock - to ensure this command is run only once at a time
            l = storage.get(self.cachelock)
            if l is not None:
                return

            storage.set(self.cachelock, self.cachelock, self.cachelock_timeout)

        if self.pid_file is not None:
            if path.exists(self.pid_file):
                # kill my predecessor
                f = open(self.pid_file)
                pid = f.read()
                f.close()
                try:
                    pid = int(pid)
                    kill(pid, 15)
                    time.sleep(2)
                    kill(pid, 9)
                except (ValueError, OSError), e:
                    pass

            # write my pid file
            f = open(self.pid_file, 'w')
            f.write(str(getpid()))
            f.close()

        # call logic of this command
        self.logic(*args, **options)

        if self.pid_file is not None:
            remove(self.pid_file)

        if self.cachelock is not None:
            # delete lock
            storage.delete(self.cachelock)

        # call return function
        self.out()

