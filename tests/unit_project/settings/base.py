from os.path import dirname, join, normpath, pardir

USE_I18N = True

FILE_ROOT = normpath(join(dirname(__file__), pardir))

MEDIA_ROOT = join(FILE_ROOT, 'static')

MEDIA_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/admin_media/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'unit_project.template_loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'unit_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(FILE_ROOT, 'templates'),

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'mypage.context_processors.mypage',
)

INSTALLED_APPS = (
    # main apps
    'mypage.widgets',
    'mypage.pages',
    # test widget app
    'unit_project.testwidgets',
    # apps for particular widget tests
    'mypage.rsswidgets',
    # django contrib apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.admin',
)

DEFAULT_PAGE_ID = 1

VERSION = 1

MOBILE_DOMAIN = 'http://mobile.example.com/'

MYPAGE_WEATHER_SOURCE_URL = join(FILE_ROOT, 'data', 'weatherwidget-090107.source')

MYPAGE_XMLSOURCEWIDGET_SOURCE_URL_PATTERN = join(FILE_ROOT, 'data', 'test_xml_%s.source')

MYPAGE_CURRENCYWIDGET_SOURCE_URL_PATTERN = join(FILE_ROOT, 'data', 'currencywidget_%s.source')

MYPAGE_HOROSCOPEWIDGET_SOURCE_URL_PATTERN = join(FILE_ROOT, 'data', 'horoscopewidget_%s.source')

MYPAGE_RADIOWIDGET_SOURCE_URL_PATTERN = join(FILE_ROOT, 'data', 'radiowidget_%s.source')

MYPAGE_PREPNITVPROGRAMWIDGET_SOURCE_URL_PATTERN = join(FILE_ROOT, 'data', 'prepnitvprogramwidget_%s.source')

MYPAGE_BOOKMARKWIDGET_DOCUMENT_TO_FETCH_TITLE_URL_PATTERN = "file://%s" % join(FILE_ROOT, 'data', 'bookmarkwidget_document_to_fetch_title_%s.html')

EXAMPLE_RSS_FEED = join(FILE_ROOT, 'data', 'example.rss')

