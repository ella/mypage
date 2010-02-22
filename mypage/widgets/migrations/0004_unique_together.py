
from south.db import db
from django.db import models
from mypage.widgets.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Creating unique_together for [widget, state, site] on RenderedWidget.
        db.create_unique('widgets_renderedwidget', ['widget_id', 'state', 'site_id'])
        
        # Deleting unique_together for [widget, state] on RenderedWidget.
        db.delete_unique('widgets_renderedwidget', ('widget_id', 'state'))
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [widget, state, site] on RenderedWidget.
        db.delete_unique('widgets_renderedwidget', ['widget_id', 'state', 'site_id'])
        
        # Creating unique_together for [widget, state] on RenderedWidget.
        db.create_unique('widgets_renderedwidget', ('widget_id', 'state'))
        
    
    
    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'widgets.renderedwidget': {
            'Meta': {'unique_together': "(('widget','state','site',),)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'rendered_html': ('models.TextField', [], {}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {'default': ' lambda :settings.SITE_ID'}),
            'state': ('models.SmallIntegerField', [], {'default': '0'}),
            'widget': ('models.ForeignKey', ["orm['widgets.Widget']"], {'verbose_name': "_('Widget')"})
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
            'shared': ('models.BooleanField', ["_('Shared')"], {'default': 'True'}),
            'slug': ('models.SlugField', [], {'max_length': '100'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '100'}),
            'url': ('models.URLField', ["_('Header link URL')"], {'blank': 'True'})
        }
    }
    
    complete_apps = ['widgets']
