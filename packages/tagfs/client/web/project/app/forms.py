# -*- coding: utf-8 -*-

# Create your forms here.

from django import forms
from django.utils.translation import ungettext, ugettext_lazy as _

class UploadForm(forms.ModelForm):
    """
    Form para subir los ficheros.
    """
    name            = forms.CharField(label=_('Nombre'), max_length=50)
    description     = forms.CharField(label=_('Descripción'), widget=forms.Textarea, max_length=500)
    tags            = forms.CharField(label=_('Tags'), max_length=50)
    data            = forms.FileField(label=_('Archivo'), widget=forms.FileInput)
    replication     = forms.IntegerField(widget=forms.HiddenInput)    
    
    def __unicode__(self):
        return self.name

class ListForm(forms.ModelForm):
    """
    Form para listar los ficheros que tienen todos los tags especificados.
    """
    tags            = forms.CharField(label='Tags', max_length=50)
    
    def __unicode__(self):
        return self.tags

class SearchForm(forms.ModelForm):
    """
    Form para busqueda de texto libre.
    """
    text            = forms.CharField(label='Texto', max_length=250)
    
    def __unicode__(self):
        return self.text