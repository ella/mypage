
from south.db import db
from django.db import models
from mypage.widgets.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'RenderedWidget'
        db.create_table('widgets_renderedwidget', (
            ('id', models.AutoField(primary_key=True)),
            ('widget', models.ForeignKey(orm.Widget, verbose_name=_('Widget'))),
            ('state', models.SmallIntegerField(default=0)),
            ('rendered_html', models.TextField()),
        ))
        db.send_create_signal('widgets', ['RenderedWidget'])
        
        # Adding model 'Widget'
        db.create_table('widgets_widget', (
            ('id', models.AutoField(primary_key=True)),
            ('content_type', ContentTypeField(editable=False)),
            ('title', models.CharField(_('Title'), max_length=100)),
            ('slug', models.SlugField(max_length=100)),
            ('last_downloaded', models.DateTimeField(null=True, blank=True)),
            ('next_download', models.DateTimeField(default=datetime.datetime.now)),
            ('url', models.URLField(_('Header link URL'), blank=True)),
            ('shared', models.BooleanField(_('Shared'), default=True)),
        ))
        db.send_create_signal('widgets', ['Widget'])
        
        # Creating unique_together for [widget, state] on RenderedWidget.
        db.create_unique('widgets_renderedwidget', ['widget_id', 'state'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'RenderedWidget'
        db.delete_table('widgets_renderedwidget')
        
        # Deleting model 'Widget'
        db.delete_table('widgets_widget')
        
        # Deleting unique_together for [widget, state] on RenderedWidget.
        db.delete_unique('widgets_renderedwidget', ['widget_id', 'state'])
        
    
    
    models = {
        'widgets.renderedwidget': {
            'Meta': {'unique_together': "(('widget','state',),)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'rendered_html': ('models.TextField', [], {}),
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
