#encoding:utf-8
from django.db import models
from django.utils.encoding import smart_unicode, iri_to_uri
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.contrib.admin.filterspecs import FilterSpec
from service.core import _dealer

import datetime
import mc
from mc.models import Term

AREA_VAR = 'area'
DEALER_TYPE_VAR = 'dealertype'
TERM_VAR = 'termid'
from models import Paper, Dealer, DealerType

FilterSpec.register_first = classmethod(lambda cls, test, factory: cls.filter_specs.insert(0, (test, factory)))

class AreaFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin):
        super(AreaFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_title = u'区域'
        #rel_name = f.rel.get_related_field().name
        #c = f.name
        #xx = f.rel.get_related_field()
        
        self.lookup_kwarg = AREA_VAR
        self.lookup_val = request.GET.get(AREA_VAR, None)
        self.lookup_choices = _dealer.get_regionals()
    
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
                   'display': up.name_cn}
    
FilterSpec.register_first(lambda f: bool(f.name == 'visit_begin'), AreaFilterSpec)

class DealerTypeFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin):
        super(DealerTypeFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_title = u'经销商'
        #rel_name = f.rel.get_related_field().name
        #c = f.name
        #xx = f.rel.get_related_field()
        
        self.lookup_kwarg = DEALER_TYPE_VAR
        self.lookup_val = request.GET.get(DEALER_TYPE_VAR, None)
        self.lookup_choices = DealerType.objects.all().order_by('id')
    
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
                   'display': up.name_cn}
    
FilterSpec.register_first(lambda f: bool(f.name == 'visit_end'), DealerTypeFilterSpec)

class TermFilterSpec(FilterSpec):
    def __init__(self, f, request, params, model, model_admin):
        super(TermFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_title = u'期数'
        #rel_name = f.rel.get_related_field().name
        #c = f.name
        #xx = f.rel.get_related_field()
        
        self.lookup_kwarg = TERM_VAR
        self.lookup_val = request.GET.get(TERM_VAR, None)
        self.lookup_choices = Term.objects.filter(id__gt=4).order_by('id')
    
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
                   'display': up.name_cn}
    
FilterSpec.register_first(lambda f: bool(f.name == 'survey_code'), TermFilterSpec)
