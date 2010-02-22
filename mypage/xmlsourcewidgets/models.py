import urllib
import logging
from cStringIO import StringIO

from mypage.widgets.models import Widget, WidgetFetchDataFailedException


log = logging.getLogger('mypage.xmlsourcewidgets.models')
sourceslog = logging.getLogger('mypage.widgets.models.sources')


class SourceValidationError(Exception):
    pass


class SourceValidationWarning(UserWarning):
    pass


class BaseXMLSourceWidget(Widget):

    source_url = ''

    fetch_source_exeptions = (IOError,)
    parse_source_exeptions = (Exception,)

    SourceValidationError = SourceValidationError
    SourceValidationWarning = SourceValidationWarning
    # TODO do this on Widget class (move it there)
    WidgetFetchDataFailedException = WidgetFetchDataFailedException

    class Meta:
        abstract = True

    def fetch_source(self):
        return StringIO(urllib.urlopen(self.source_url).read())

    def parse_source(self, source):
        raise NotImplementedError()

    def validate_source(self, source):
        pass

    def _fetch_data(self):
        try:
            source = self.fetch_source()
            data = self.parse_source(source)
        except self.fetch_source_exeptions, e:
            message = "Widget %s fetch source failed (%s: %s)" % (self.pk, e.__class__.__name__, e)
            log.warn(message)
            raise self.WidgetFetchDataFailedException(message)
        except self.parse_source_exeptions, e:
            message = "Widget %s parse source failed (%s: %s)" % (self.pk, e.__class__.__name__, e)
            log.error(message)
            sourceslog.warn("%s\n\n%s" % (message, source.read()))
            raise self.WidgetFetchDataFailedException(message)
        try:
            self.validate_source(data)
        except self.SourceValidationError, e:
            message = "Widget %s source validation failed (%s)" % (self.pk, e)
            log.error(message)
            sourceslog.warn("%s\n\n%s" % (message, source.read()))
            raise self.WidgetFetchDataFailedException(message)
        except self.SourceValidationWarning, e:
            message = "Widget %s source validation failed (%s). Skipped. Data fetched." % (self.pk, e)
            log.warn(message)
            sourceslog.warn("%s\n\n%s" % (message, source.read()))
        return data

