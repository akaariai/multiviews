# Create your views here.
import inspect
from django import forms
from django.conf.urls.defaults import patterns, url, include
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from .models import SingleField, MultiField

class CreateUrlsMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super(CreateUrlsMeta, cls).__new__(cls, name, bases, attrs)
        new_cls.url_patterns = patterns('',)
        for attr_name, func in inspect.getmembers(new_cls, inspect.ismethod):
            if hasattr(func, 'url'):
                setattr(new_cls, attr_name + '_urlname', attrs['namespace'] + ':' + attr_name)
                new_cls.url_patterns.append(url(func.url, new_cls.view, name=attr_name))
        return new_cls


class MultiView(object):
    __metaclass__ = CreateUrlsMeta

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def view(cls, request, *args, **kwargs):
        instance = cls(request, *args, **kwargs)
        instance.view_name = request.resolver_match.url_name
        view_func = getattr(instance, request.resolver_match.url_name)
        return view_func(request, *args, **kwargs)

class ObjectMultiView(MultiView):
    namespace = ''

    def create(self, request):
        if request.method == 'POST':
            form = self.new_form(request.POST)
            if form.is_valid():
                obj = form.save()
                return HttpResponseRedirect(
                    reverse(self.details_urlname, args=(obj.pk,)))
        else:
            form = self.new_form()
        return self.render_to_response(self.new_template, {'form': form})
    create.url = r'^new/$'

    def modify(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        if request.method == 'POST':
            form = self.edit_form(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse(self.details_urlname, args=(obj.pk,)))
        else:
            form = self.edit_form(instance=obj)
        return self.render_to_response(
            self.new_template, {'form': form, 'obj': obj})
    modify.url = r'^edit/(\d+)/$'

    def details(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        ctx_data = self.ctx_data(obj=obj)
        return self.render_to_response(
            self.details_template, ctx_data)
    details.url = r'^details/(\d+)/$'

    def ctx_data(self, **kwargs):
        return kwargs

    def list(self, request):
        objs = self.model.objects.all()
        return self.render_to_response(
            self.list_template, {'objects': objs})
    list.url = r'^$'

    def render_to_response(self, template, context_data):
        context_data.update({'view': self})
        return render_to_response(
            template, context_data, RequestContext(self.request))

    @classmethod
    def urls(cls, prefix):
        return url(prefix, include(cls.url_patterns, namespace=cls.namespace))

class SingleFieldForm(forms.ModelForm):
    class Meta:
        model = SingleField

class SingleFieldViews(ObjectMultiView):
    model = SingleField
    new_form = edit_form = SingleFieldForm
    namespace = 'singlefield'
    new_template = edit_template = 'obj_edit.html'
    details_template = 'singlefield/details.html'
    list_template = 'obj_list.html'

class MultiFieldForm(forms.ModelForm):
    class Meta:
        model = MultiField

class MultiFieldViews(ObjectMultiView):
    model = MultiField
    new_form = edit_form = MultiFieldForm
    namespace = 'multifield'
    new_template = edit_template = 'obj_edit.html'
    details_template = 'multifield/detail.html'
    list_template = 'obj_list.html'

    def ctx_data(self, **kwargs):
        if self.view_name == 'details':
            obj = kwargs['obj']
            kwargs['obj_data'] = [(f.verbose_name, getattr(obj, f.name)) for f in obj._meta.fields]
        return kwargs

    def details_compact(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        return self.render_to_response(
            'multifield/compact_details.html', {'obj': obj})
    details_compact.url = r'^details_compact/(\d+)/$'
