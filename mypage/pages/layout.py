import itertools
from copy import deepcopy

from django.utils.hashcompat import md5_constructor
from django.utils.safestring import mark_safe

from mypage.widgets.models import Widget, RenderedWidget
from mypage.widgets.models import get_object
from mypage.widgets.templatetags.splitobjectlist import split_list
from mypage.pages.conf import settings

class Layout(dict):

    class WidgetInLayoutDoesNotExist(Exception): pass

    def __init__(self, page, *args, **kwargs):
        super(Layout, self).__init__(*args, **kwargs)
        self.changed = False
        self.page = page
        self['containers'] = [Container(self, c) for c in self.setdefault('containers', [])]
        self['static_containers'] = [StaticContainer(self, c) for c in self.setdefault('static_containers', [])]
        #self['template_config'] = TemplateConfig(self, self.setdefault('template_config', {}))
        # TODO after page.skin mimgration raplace line below by the line above
        self['template_config'] = TemplateConfig(self, self.setdefault('template_config', self.auto_migrate_tpl_config()))

    def auto_migrate_tpl_config(self):
        """
        Temporary automigration method migrates skin option from page.skin field
        """
        # TODO remove this method def after pake.skin migration
        if not 'template_config' in self:
            self['template_config'] = dict(skin=self.page.skin or 'default')

    @property
    def containers(self):
        return self['containers']

    @property
    def static_containers(self):
        return self['static_containers']

    @property
    def template_config(self):
        return self['template_config']

    @property
    def dynamic_widgets(self):
        return list(itertools.chain(*self.containers))

    @property
    def static_widgets(self):
        return list(itertools.chain(*self.static_containers))

    @property
    def widgets(self):
        return self.dynamic_widgets + self.static_widgets

    def save(self):
        self.page.layout = self
        self.changed = True

    def render(self, context, settab=None):
        """
        Returns layout containers filled with rendered widgets
        """
        def checktab(settab, widget_ct_id, widget_id):
            if settab and (int(settab['widget_ct_id']), int(settab['widget_id'])) == (widget_ct_id, widget_id):
                return settab['tab']
            return None
        layout = {}
        for k in ('static_containers', 'containers',):
            layout[k] = [ [wil.render(context, tab=checktab(settab, wil.widget_ct_id, wil.widget_id)) for wil in c] for c in self[k] ]
        return layout

    def insert_widget(self, widget, container=0, position=None, config=None, state=None):
        """
        Inserts widget to given position

        If allready assigned, it does nothing.
        """
        if not self.contains_widget_by_instance(widget):
            container = int(container) # FIXME IMHO may be in view function somewhere :)
            container = self.containers[container] # may raise Index/ValueError
            container.insert_widget(widget, position, config, state)

    def contains_widget(self, widget_ct_id, widget_id):
        try:
            self.get_widget(widget_ct_id, widget_id)
            return True
        except self.WidgetInLayoutDoesNotExist, e:
            return False
    
    def contains_widget_by_instance(self, widget):
        return self.contains_widget(widget.content_type_id, widget.pk)

    def remove_widget(self, widget):
        """
        Removes all found widget's wils
        """
        for container in self.containers:
            container.remove_widget(widget)

    def get_widget_by_instance(self, widget):
        """
        Returns WIL by given widget instance
        """
        return self.get_widget(widget.content_type_id, widget.pk)

    def get_widget(self, widget_ct_id=None, widget_id=None):
        """
        Returns WIL by given keys
        """
        for wil in self.widgets:
            if (wil.widget_ct_id, wil.widget_id) == (widget_ct_id, widget_id):
                return wil
        raise self.WidgetInLayoutDoesNotExist("WidgeInLayout with given keys does not exist!")

    def configure_widget(self, widget_ct_id, widget_id, data):
        """
        Configures WIL found in containers
        """
        wil = self.get_widget(widget_ct_id, widget_id)
        return wil.configure(data)

    def configure_widget_by_instance(self, widget):
        return self.configure_widget(widget.content_type_id, widget.pk)

    def arrange_containers(self, cols):
        """
        Splits widgets to given number of containers
        """
        self['containers'] = split_list(self.dynamic_widgets, cols)
        self.save()

    def arrange_widgets(self, containers):
        """
        Updates widggets positions in containers

        Widgets can be placed and removed via this method.
        """
        new_containers = []
        for container in containers:
            new_container = Container(self, [])
            for widget_ct_id, widget_id in container:
                try:
                    wil = self.get_widget(widget_ct_id, widget_id)
                except self.WidgetInLayoutDoesNotExist, e:
                    widget = get_object(widget_ct_id, widget_id) # existence check
                    wil = WidgetInLayout.factory(new_container, widget)
                new_container.append(wil)
            new_containers.append(new_container)
        self['containers'] = new_containers
        self.save()
        return self.containers

    def clone(self):
        return deepcopy(self)


class Container(list):
    
    def __init__(self, layout, widgets):
        self.layout = layout
        return super(Container, self).__init__([WidgetInLayout(self, w) for w in widgets])

    def save(self):
        self.layout.save()

    def insert_widget(self, widget, position=None, config=None, state=None):
        wil = WidgetInLayout.factory(self, widget, config, state)
        if position is not None:
            self.insert(position, wil)
        else:
            self.append(wil)
        self.save()

    def remove_widget(self, widget):
        for wil in self:
            if (wil.widget_ct_id, wil.widget_id)  == (widget.content_type_id, widget.pk):
                self.remove(wil)
        self.save()


class StaticContainer(Container):
    pass


class WidgetInLayout(dict):

    STATE_NORMAL = 0
    STATE_NEW = 2
    STATE_MINIMIZED = 1

    def __init__(self, container, *args, **kwargs):
        self.container = container
        return super(WidgetInLayout, self).__init__(*args, **kwargs)

    @property
    def widget_ct_id(self):
        return self['widget_ct_id']

    @property
    def widget_id(self):
        return self['widget_id']

    def config_get(self):
        return self['config']
    def config_set(self, value):
        self['config'] = value
        self.save()
    config = property(config_get, config_set)

    def state_get(self):
        return self['state']
    def state_set(self, value):
        self['state'] = value
        self.save()
    state = property(state_get, state_set)

    @property
    def widget(self):
        return get_object(self.widget_ct_id, self.widget_id)

    def render(self, context={}, allow_fetch=False, tab=None):
        if self.state == self.STATE_NEW:
            self.state = self.STATE_NORMAL
        rendered_widget = self.widget.rendered_widget_class(self.widget, self.state)
        return mark_safe(rendered_widget.render(self.config, context, allow_fetch, tab=tab))

    def configure(self, data, widget_config_function=None):
        if widget_config_function is None:
            widget_config_function = self.widget.get_widget_in_page_configuration
        if self.config in ('', None):
            self.config = {}
        self.config = widget_config_function(self.config or {}, data)
        self.save()

    def save(self):
        self.container.save()

    @classmethod
    def factory(cls, container, widget, config=None, state=None):
        if state is None:
            state = cls.STATE_NEW
        return cls(container, dict(
            widget_ct_id = widget.content_type_id,
            widget_id = widget.pk,
            config = config or {},
            state = state
        ))


class TemplateConfig(dict):

    options = settings.PAGE_TEMPLATE_OPTIONS

    def __init__(self, layout, *args, **kwargs):
        self.layout = layout
        super(TemplateConfig, self).__init__(*args, **kwargs)

    def save(self):
        self.layout.save()

    def as_hash(self):
        return md5_constructor(self.__str__()).hexdigest()

    def __getitem__(self, key):
        try:
            return super(TemplateConfig, self).__getitem__(key)
        except KeyError, e:
            return self.get_default(key)

    @classmethod
    def get_default(cls, key):
        try:
            return cls.options[key][1]
        except KeyError, e:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("Template option \"%s\" is not defined. Check PAGE_TEMPLATE_OPTIONS in your settings (Format: PAGE_TEMPLATE_OPTIONS = {<option_name>: (<choice_list>, <default_value>)})" % key)
