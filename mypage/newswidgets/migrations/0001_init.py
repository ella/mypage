
from south.db import db
from django.db import models
from mypage.newswidgets.models import *

class Migration:
    
    depends_on = (
        ("rsswidgets", "0001_init"),
    )
    
    def forwards(self, orm):
        
        # Adding model 'NewsSource'
        db.create_table('newswidgets_newssource', (
            ('id', models.AutoField(primary_key=True)),
            ('widget', models.ForeignKey(orm.NewsWidget)),
            ('rsswidget', models.ForeignKey(orm['rsswidgets.RSSWidget'], verbose_name=_('RSSWidget with feed source'))),
            ('name', models.CharField(max_length=255)),
            ('slug', models.SlugField(max_length=255)),
            ('url', models.URLField(max_length=255, null=True, blank=True)),
            ('order', models.PositiveIntegerField(unique=True)),
            ('item_count', models.PositiveIntegerField()),
        ))
        db.send_create_signal('newswidgets', ['NewsSource'])
        
        # Adding model 'NewsWidget'
        db.create_table('newswidgets_newswidget', (
            ('widget_ptr', models.OneToOneField(orm['widgets.Widget'])),
            ('rsswidget', models.ForeignKey(orm['rsswidgets.RSSWidget'], verbose_name=_('RSSWidget with feed source for perex'))),
        ))
        db.send_create_signal('newswidgets', ['NewsWidget'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'NewsSource'
        db.delete_table('newswidgets_newssource')
        
        # Deleting model 'NewsWidget'
        db.delete_table('newswidgets_newswidget')
        
    
    
    models = {
        'widgets.widget': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'newswidgets.newssource': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'item_count': ('models.PositiveIntegerField', [], {}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'order': ('models.PositiveIntegerField', [], {'unique': 'True'}),
            'rsswidget': ('models.ForeignKey', ["orm['rsswidgets.RSSWidget']"], {'verbose_name': "_('RSSWidget with feed source')"}),
            'slug': ('models.SlugField', [], {'max_length': '255'}),
            'url': ('models.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'widget': ('models.ForeignKey', ["orm['newswidgets.NewsWidget']"], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'newswidgets.newswidget': {
            'Meta': {'_bases': ['mypage.widgets.models.Widget']},
            'rsswidget': ('models.ForeignKey', ["orm['rsswidgets.RSSWidget']"], {'verbose_name': "_('RSSWidget with feed source for perex')"}),
            'widget_ptr': ('models.OneToOneField', ["orm['widgets.Widget']"], {})
        },
        'rsswidgets.rsswidget': {
            'Meta': {'_bases': ['mypage.widgets.models.Widget']},
            '_stub': True,
            'widget_ptr': ('models.OneToOneField', ["orm['widgets.Widget']"], {})
        }
    }
    
    complete_apps = ['newswidgets']
