# -*- coding: utf-8 -*-

# Create your forms here.

from django import forms

class UploadForm(forms.Form):
    """
    Form para subir los ficheros.
    """
    name            = forms.CharField(label='Nombre *', max_length=50)
    description     = forms.CharField(label='Descripción *', widget=forms.Textarea, max_length=500)
    tags            = forms.CharField(label='Tags *', max_length=50)
    data            = forms.FileField(label='Archivo *', widget=forms.FileInput)
    replication     = forms.IntegerField(label='% de replicación', required=False)

    def __unicode__(self):
        return self.name

class ListForm(forms.Form):
    """
    Form para listar los ficheros que tienen todos los tags especificados.
    """
    tags            = forms.CharField(label='Tags', max_length=50)

    def __unicode__(self):
        return self.tags

class SearchForm(forms.Form):
    """
    Form para busqueda de texto libre.
    """
    text            = forms.CharField(label='Texto', max_length=250)

    def __unicode__(self):
        return self.text