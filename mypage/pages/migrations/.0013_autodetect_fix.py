
from south.db import db
from django.db import models
from mypage.pages.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'pages.page': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'layout_json': ('models.TextField', [], {}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID'}),
            'skin': ('models.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'template': ('models.CharField', [], {'default': "'page.html'", 'max_length': '100'})
        },
        'pages.userpage': {
            'Meta': {'unique_together': "(('site_copy','user',),)", '_bases': ['mypage.pages.models.Page']},
            'page_ptr': ('models.OneToOneField', ["orm['pages.Page']"], {}),
            'site_copy': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'db_index': 'True'})
        },
        'pages.sessionpage': {
            'Meta': {'unique_together': "(('site_copy','session_key',),)", '_bases': ['mypage.pages.models.Page']},
            'page_ptr': ('models.OneToOneField', ["orm['pages.Page']"], {}),
            'session_key': ('models.CharField', ["_('session key')"], {'max_length': '40', 'db_index': 'True'}),
            'site_copy': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID'}),
            'updated': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'False'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['pages']
