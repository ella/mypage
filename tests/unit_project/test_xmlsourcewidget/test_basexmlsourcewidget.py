from lxml import etree
from unittest import TestCase

from django import forms
from django.conf import settings

from mypage.xmlsourcewidgets.models import BaseXMLSourceWidget

class TestXMLSourceWidget(BaseXMLSourceWidget):
    def parse_source(self, source):
        data = []
        for e in etree.parse(source).xpath('/items/item'):
            data.append(dict([(e.tag, e.text) for e in e.getchildren()]))
        return data


class TestBaseXMLSourceWidget(TestCase):

    def setUp(self):
        """
        Widget creation
        
        Widget is not saved into db. Method update_next_download() called in fetch_data()
        makes update on empty queryset.
        """
        self.widget = TestXMLSourceWidget(title='test', slug='test')

    def test_fetch_data_source_fetching_failed(self):
        """
        Test fetch_data source fetching failure

        No source found
        """
        self.widget.source_url = '/there/is/no/source/'
        self.failUnlessRaises(IOError, self.widget.fetch_source)
        self.failUnlessRaises(self.widget.WidgetFetchDataFailedException, self.widget.fetch_data)

    def test_fetch_data_source_parsing_failed(self):
        """
        Test fetch_data source parsing failure

        Source found and readed
        XML parsing failed
        """
        self.widget.source_url = settings.MYPAGE_XMLSOURCEWIDGET_SOURCE_URL_PATTERN % 'invalid'
        self.failUnlessEqual('an invalid xml source\n', self.widget.fetch_source().read())
        self.failUnlessRaises(self.widget.WidgetFetchDataFailedException, self.widget.fetch_data)

    def test_fetch_data_source_validation_failed(self):
        """
        Test fetch_data source validation failure

        Source found and readed
        XML parsed and validated
        Data validation failed
        """
        def validate_source(source):
            raise self.widget.SourceValidationError()
        self.widget.source_url = settings.MYPAGE_XMLSOURCEWIDGET_SOURCE_URL_PATTERN % 'valid'
        self.widget.validate_source = validate_source
        self.failUnless(isinstance(self.widget.fetch_source().read(), basestring))
        self.failUnlessRaises(self.widget.WidgetFetchDataFailedException, self.widget.fetch_data)

    def test_fetch_data_success(self):
        """
        Test fetch_data source validation failure

        Source found and readed
        XML parsed and validated
        Data validation success
        """
        self.widget.source_url = settings.MYPAGE_XMLSOURCEWIDGET_SOURCE_URL_PATTERN % 'valid'
        self.failUnlessEqual([{'testfield': 'test value', 'othertestfield': 'other test value'}], self.widget.fetch_data())

