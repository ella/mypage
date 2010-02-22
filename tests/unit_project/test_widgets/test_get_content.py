from djangosanetesting import UnitTestCase

from django.contrib.contenttypes.models import ContentType

from mypage.widgets.models import Widget

from unit_project import template_loader

class TestGetContent(UnitTestCase):
    def setUp(self):
        self.templates = template_loader.templates.copy()
        template_loader.templates.update({
            'widgets.widget/widget.html': '',
            'widgets.widget/content.html': 'content',
        })
        wct = ContentType.objects.get_for_model(Widget)
        self.w = Widget(content_type=wct)

    def test_getcontent_empty_widget_returns_value(self):
        content = self.w.get_content({}, {}, allow_fetch=True)
        self.assert_equals('content', content)

    def tearDown(self):
        template_loader.templates = self.templates

