from django.conf.urls.defaults import *

from mypage.pages import views

urlpatterns = patterns('',
    url(r'^$', views.home_page, name='home_page'),
    url(r'^action/(\d+)/(\d+)/([\w-]+)/$', views.widget_action, name='widget_action'),
    url(r'^configure/(\d+)/(\d+)/$', views.configure_widget, name='configure_widget'),
    url(r'^update_layout/$', views.update_layout, name='update_layout'),
    url(r'^set_state/(\d+)/(\d+)/$', views.set_state, name='set_state'),
    url(r'^skinit/(\w*)/?$', views.skinit, name='skinit'),
    url(r'^add_widget/([\w-]+)/$', views.add_widget, name='add_widget'),
    url(r'^get_content/(\d+)/(\d+)/$', views.get_content, name='get_content'),
    url(r'^get_display_form/(\d+)/(\d+)/$', views.get_display_form, name='get_display_form'),

    url(r'^reset_page/$', views.reset_page, name='reset_page'),
    url(r'^set_theme/([\w-]+)/$', views.set_theme, name='set_theme'),

    url(r'^setup_template/$', views.SetupPageTemplateView(), name='setup_page_template'),
    url(r'^setup_template_config/$', views.SetupPageTemplateConfigView(), name='setup_page_template_config'),
    url(r'^reset_template/$', views.reset_page_template, name='reset_page_template'),
    url(r'^reset_template_config/$', views.reset_page_template_config, name='reset_page_template_config'),

    url(r'^setup_page_widgets/$', views.setup_page_widgets, name='setup_page_widgets'),

)
