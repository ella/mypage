from os import path
import tempfile

from mypage.utils.settings import Settings

MYPAGE_COMMAND_CACHELOCK = 'command_cachelock'
MYPAGE_COMMAND_CACHELOCK_TIMEOUT = 2*60
MYPAGE_COMMAND_PIDFILE = path.join(tempfile.gettempdir(), 'command.pid')

MYPAGE_FETCH_CACHELOCK = 'fetch_cachelock'
MYPAGE_FETCH_PIDFILE = path.join(tempfile.gettempdir(), 'fetch.pid')

settings = Settings('mypage.widgets.conf')

