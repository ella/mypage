from django.db import models

import anyjson as json

class JSONField(models.TextField):
    """
    Stores data in JSON format
    """
    __metaclass__ = models.SubfieldBase

    def db_type(self):
        return "TextField"

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        return json.serialize(value)

    def to_python(self, value):
#        return value # TODO: uncomment this if you're doing dumpdata or loaddata
        if (value == ""):
            return {}
        elif (isinstance(value, (str, unicode))):
            return json.deserialize(value)
        else:
            return value

# TODO: whoa? is this working or not
#    def get_db_prep_value(self, value):
#        return json.serialize(value)
#
#    def value_to_string(self, obj):
#        value = self._get_val_from_obj(obj)
#        return self.get_db_prep_value(value)


from django.db.models.fields.related import ForeignKey, ReverseSingleRelatedObjectDescriptor
from django.contrib.contenttypes.models import ContentType

class ContentTypeField( ForeignKey ):
    def __init__(self, *args, **kwargs):
        super(ContentTypeField, self).__init__(ContentType, *args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(ContentTypeField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, ContentTypeObjectDescriptor(self))

class ContentTypeObjectDescriptor( ReverseSingleRelatedObjectDescriptor ):
    def __get__(self, instance, instance_type=None):
        if instance is None:
            raise AttributeError, "%s must be accessed via instance" % self.field.name
        cache_name = self.field.get_cache_name()
        try:
            return getattr(instance, cache_name)
        except AttributeError:
            val = getattr(instance, self.field.attname)
            if val is None:
                # If NULL is an allowed value, return it.
                if self.field.null:
                    return None
                raise self.field.rel.to.DoesNotExist
            rel_obj = ContentType.objects.get_for_id(val)
            setattr(instance, cache_name, rel_obj)
            return rel_obj

