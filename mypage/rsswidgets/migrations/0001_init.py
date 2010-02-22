
from south.db import db
from django.db import models
from mypage.rsswidgets.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'RSSWidget'
        db.create_table('rsswidgets_rsswidget', (
            ('widget_ptr', models.OneToOneField(orm['widgets.Widget'])),
            ('feed_url', models.URLField()),
            ('frequency_seconds', models.PositiveIntegerField(default=1800)),
        ))
        db.send_create_signal('rsswidgets', ['RSSWidget'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'RSSWidget'
        db.delete_table('rsswidgets_rsswidget')
        
    
    
    models = {
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
        'widgets.widget': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['rsswidgets']
