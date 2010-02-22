
from south.db import db
from django.db import models
from mypage.rsswidgets.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'MultiRSSWidget.config_json'
        db.add_column('rsswidgets_multirsswidget', 'config_json', models.TextField())
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'MultiRSSWidget.config_json'
        db.delete_column('rsswidgets_multirsswidget', 'config_json')
        
    
    
    models = {
        'widgets.widget': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'rsswidgets.rsswidget': {
            'Meta': {'_bases': ['mypage.widgets.models.Widget']},
            'feed_url': ('models.URLField', [], {}),
            'frequency_seconds': ('models.PositiveIntegerField', [], {'default': '1800'}),
            'widget_ptr': ('models.OneToOneField', ["orm['widgets.Widget']"], {})
        },
        'rsswidgets.multirsswidget': {
            'Meta': {'_bases': ['mypage.widgets.models.Widget']},
            'config_json': ('models.TextField', [], {}),
            'widget_ptr': ('models.OneToOneField', ["orm['widgets.Widget']"], {})
        }
    }
    
    complete_apps = ['rsswidgets']
