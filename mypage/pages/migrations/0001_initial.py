
from south.db import db
from django.db import models
from mypage.pages.models import *
import datetime

class Migration:

    depends_on = (
        ("widgets", "0001_initial"),
    )
    
    def forwards(self, orm):
        
        # Adding model 'Page'
        db.create_table('pages_page', (
            ('id', models.AutoField(primary_key=True)),
            ('template', models.CharField(default='page.html', max_length=100)),
            ('skin', models.CharField(default='', max_length=100, blank=True)),
            ('layout_json', models.TextField()),
        ))
        db.send_create_signal('pages', ['Page'])
        
        # Adding model 'WidgetInPage'
        db.create_table('pages_widgetinpage', (
            ('id', models.AutoField(primary_key=True)),
            ('page', models.ForeignKey(orm.Page, verbose_name=_('Page'))),
            ('rendered_widget', models.ForeignKey(orm['widgets.RenderedWidget'], null=False)),
            ('widget', models.ForeignKey(orm['widgets.Widget'], verbose_name=_('Widget'))),
            ('config_json', models.TextField()),
            ('state', models.SmallIntegerField(default=2)),
        ))
        db.send_create_signal('pages', ['WidgetInPage'])
        
        # Adding model 'UserPage'
        db.create_table('pages_userpage', (
            ('page_ptr', models.OneToOneField(orm['pages.Page'])),
            ('user', models.ForeignKey(orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('pages', ['UserPage'])
        
        # Adding model 'SessionPage'
        db.create_table('pages_sessionpage', (
            ('page_ptr', models.OneToOneField(orm['pages.Page'])),
            ('session_key', models.CharField(_('session key'), unique=True, max_length=40)),
            ('updated', models.DateTimeField(default=datetime.datetime.now, null=False)),
        ))
        db.send_create_signal('pages', ['SessionPage'])
        
        # Creating unique_together for [page, widget] on WidgetInPage.
        db.create_unique('pages_widgetinpage', ['page_id', 'widget_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('pages_page')
        
        # Deleting model 'WidgetInPage'
        db.delete_table('pages_widgetinpage')
        
        # Deleting model 'UserPage'
        db.delete_table('pages_userpage')
        
        # Deleting model 'SessionPage'
        db.delete_table('pages_sessionpage')
        
        # Deleting unique_together for [page, widget] on WidgetInPage.
        db.delete_unique('pages_widgetinpage', ['page_id', 'widget_id'])
        
    
    
    models = {
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
            'skin': ('models.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'template': ('models.CharField', [], {'default': "'page.html'", 'max_length': '100'}),
            'widgets': ('models.ManyToManyField', ["orm['widgets.Widget']"], {'through': "'WidgetInPage'"})
        },
        'widgets.renderedwidget': {
            'Meta': {'unique_together': "(('widget','state',),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
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
        }
    }
    
    complete_apps = ['pages']
