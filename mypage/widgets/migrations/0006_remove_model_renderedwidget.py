
from south.db import db
from django.db import models
from mypage.widgets.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Deleting model 'renderedwidget'
        db.delete_table('widgets_renderedwidget')
        
    
    
    def backwards(self, orm):
        
        # Adding model 'renderedwidget'
        db.create_table('widgets_renderedwidget', (
            ('rendered_html', models.TextField()),
            ('widget', models.ForeignKey(orm['widgets.Widget'], verbose_name=_('Widget'))),
            ('site', models.ForeignKey(orm['sites.Site'], default= lambda :settings.SITE_ID)),
            ('state', models.SmallIntegerField(default=0)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('widgets', ['renderedwidget'])
        
    
    
    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
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
        }
    }
    
    complete_apps = ['widgets']
