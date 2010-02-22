
from south.db import db
from django.db import models
from django.db.models import F
from mypage.pages.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        '''
        if not db.dry_run:
            orm.UserPage.objects.update(site_copy=F('site'))
            orm.SessionPage.objects.update(site_copy=F('site'))
        '''
        db.execute('''
            update pages_userpage p JOIN pages_page ON p.page_ptr_id = pages_page.id set p.site_copy_id=site_id;
        ''')
        db.execute('''
            update pages_sessionpage p JOIN pages_page ON p.page_ptr_id = pages_page.id set p.site_copy_id=site_id;
        ''')
        
    def backwards(self, orm):
        pass
    
    
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
            'rendered_widget': ('models.ForeignKey', ["orm['widgets.RenderedWidget']"], {'null': 'False'}),
            'state': ('models.SmallIntegerField', [], {'default': '2'}),
            'widget': ('models.ForeignKey', ["orm['widgets.Widget']"], {'verbose_name': "_('Widget')"})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'widgets.widget': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'pages.page': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'layout_json': ('models.TextField', [], {}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID'}),
            'skin': ('models.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'template': ('models.CharField', [], {'default': "'page.html'", 'max_length': '100'}),
            'widgets': ('models.ManyToManyField', ["orm['widgets.Widget']"], {'through': "'WidgetInPage'"})
        },
        'widgets.renderedwidget': {
            'Meta': {'unique_together': "(('widget','state','site',),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'pages.userpage': {
            'Meta': {'_bases': ['mypage.pages.models.Page']},
            'page_ptr': ('models.OneToOneField', ["orm['pages.Page']"], {}),
            'site_copy': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID', 'null': 'True', 'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'db_index': 'True'})
        },
        'pages.sessionpage': {
            'Meta': {'_bases': ['mypage.pages.models.Page']},
            'page_ptr': ('models.OneToOneField', ["orm['pages.Page']"], {}),
            'session_key': ('models.CharField', ["_('session key')"], {'max_length': '40', 'db_index': 'True'}),
            'site_copy': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID', 'null': 'True', 'blank': 'True'}),
            'updated': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'False'})
        }
    }
    
    complete_apps = ['pages']
