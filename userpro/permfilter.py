from django.db import models
from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.admin.filterspecs import FilterSpec

import datetime

PERMS_VAR = 'perms'
from models import UserPermission

FilterSpec.register_first = classmethod(lambda cls, test, factory: cls.filter_specs.insert(0, (test, factory)))

class PermsFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin):        
        super(PermsFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_title = f.verbose_name
        #rel_name = f.rel.get_related_field().name
        #c = f.name
        #xx = f.rel.get_related_field()
        
        self.lookup_kwarg = PERMS_VAR
        self.lookup_val = request.GET.get(PERMS_VAR, None)
        self.lookup_choices = UserPermission.objects.all().order_by('id')
    
    def has_output(self):
        return len(self.lookup_choices) > 1
    
    def title(self):
        return self.lookup_title
    
    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
               'query_string': '?',
               'display': _('All')}
        for up in self.lookup_choices:
            yield {'selected': self.lookup_val == smart_unicode(up.id),
                   'query_string': cl.get_query_string({self.lookup_kwarg: up.id}),
                   'display': up.name}
    
FilterSpec.register_first(lambda f: bool(f.name == 'user_permissions'), PermsFilterSpec)

