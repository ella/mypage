from django.db import models
from mypage.pages.models import *
import datetime

from mypage.widgets.fields import ContentTypeField

from mypage.pages.migrations.utils.layout_refactor_migration import migrate


class Migration:

    no_dry_run = True
    
    def forwards(self, orm):
        migrate(Page.objects.all()[90:100])
    
    def backwards(self, orm):
        "There is no way back"
    
    
    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'pages.widgetinpage': {
            'Meta': {'unique_together': "(('page','widget',),)"},
            'config_json': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'page': ('models.ForeignKey', ["orm['pages.Page']"], {'verbose_name': "_('Page')"}),
            'state': ('models.SmallIntegerField', [], {'default': '2'}),
            'widget': ('models.ForeignKey', ["orm['widgets.Widget']"], {'verbose_name': "_('Widget')"})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'widgets.widget': {
            'content_type': ('ContentTypeField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'last_downloaded': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'next_download': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('models.SlugField', [], {'max_length': '100'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '100'}),
            'url': ('models.URLField', ["_('Header link URL')"], {'blank': 'True'})
        },
        'pages.page': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'layout_json': ('models.TextField', [], {}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID'}),
            'skin': ('models.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'template': ('models.CharField', [], {'default': "'page.html'", 'max_length': '100'}),
            'widgets': ('models.ManyToManyField', ["orm['widgets.Widget']"], {'through': "'WidgetInPage'"})
        },
        'pages.userpage': {
            'Meta': {'_bases': ['mypage.pages.models.Page']},
            'page_ptr': ('models.OneToOneField', ["orm['pages.Page']"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'unique': 'True'})
        },
        'pages.sessionpage': {
            'Meta': {'_bases': ['mypage.pages.models.Page']},
            'page_ptr': ('models.OneToOneField', ["orm['pages.Page']"], {}),
            'session_key': ('models.CharField', ["_('session key')"], {'unique': 'True', 'max_length': '40'}),
            'updated': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'False'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }
    
    complete_apps = ['pages']
