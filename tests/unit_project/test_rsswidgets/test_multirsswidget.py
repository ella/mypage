from djangosanetesting import UnitTestCase, DatabaseTestCase

from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from mypage.rsswidgets.models import RSSWidget, MultiRSSWidget

import pprint

class TestMultiRSSWidget(DatabaseTestCase):

    def setUp(self):
        super(TestMultiRSSWidget, self).setUp()

        self.rss_wct = rss_wct = ContentType.objects.get_for_model(RSSWidget)
        self.multi_wct = multi_wct = ContentType.objects.get_for_model(ContentType)

        self.rss_w = RSSWidget(title='Example RSS', slug='example-rss', content_type=rss_wct, feed_url=settings.EXAMPLE_RSS_FEED)
        self.multi_w = MultiRSSWidget(title='Test Multi RSS', slug='test-multi-rss', content_type=multi_wct)

        self.rss_w.save()

        self.data = self.rss_w.fetch_data()

        self.multi_w.config = { 'rss-widgets': [
            (self.rss_wct.id, self.rss_w.id, 1),
            (self.rss_wct.id, self.rss_w.id, 1),
        ] }
        self.multi_w.save()

    def test_multi_config_gives_correct_single_rss_items(self):
        data = self.multi_w.get_data({})
        # assert correct number of items
        self.assert_equals(2, len(data))
        # both of them the same
        self.assert_equals(u'Item Example', data[0]['item']['title'])
        self.assert_equals(u'Item Example', data[1]['item']['title'])

    def test_category_for_item_by_url(self):
        data = self.multi_w.get_data({})
        # assert category name
        self.assert_equals('Zpr\xc3\xa1vy', data[0]['category']['name'])
        self.assert_equals('Zpr\xc3\xa1vy', data[1]['category']['name'])
        # assert category url
        self.assert_equals('http://aktualne.centrum.cz', data[0]['category']['url'])
        self.assert_equals('http://aktualne.centrum.cz', data[1]['category']['url'])

