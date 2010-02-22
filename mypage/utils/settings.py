from django.utils.importlib import import_module
from django.conf import settings


class Settings(object):
    def __init__(self, module_name, prefix=''):
        self.module = import_module(module_name)
        self.prefix = prefix
    def __getattr__(self, name):
        p_name = ''.join((self.prefix, name))
        if hasattr(settings, p_name):
            return getattr(settings, p_name)
        return getattr(self.module, name)
    def __dir__(self):
        return dir(self.module) + dir(self.settings)

