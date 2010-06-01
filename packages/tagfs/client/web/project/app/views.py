# -*- coding: utf-8 -*-

# Create your views here.

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import UploadForm

HOME_TEMPLATE = 'site/home.html'
TAGS_TEMPLATE = 'site/tags.html'
PUT_TEMPLATE = 'site/put.html'

CLIENT =  settings.TAGFSCLIENT

def home(request):
    return render_to_response(HOME_TEMPLATE,
                                context_instance=RequestContext(request))


def tags(request):
    """
    Muestra todos los tags del sistema.
    """
    get_tags = request.GET.get('tags', '')

    tags = set()
    for tag in get_tags.split():
        tags.add(tag)

    objects, files = len(tags) and (CLIENT.list(tags), True) or (CLIENT.get_all_tags(), False)

    return render_to_response(TAGS_TEMPLATE,
                                { 'tags': tags, 'objects': objects, 'files': files },
                                context_instance=RequestContext(request))


def put(request):
    """
    Se ocupa de poner un fichero en tagfs, 
    verificando que se cumplen todos los requisitos del form.
    """
    form = UploadForm()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            tags_cleaned = form.cleaned_data['tags']
            data = form.cleaned_data['data']
            replication = form.cleaned_data['replication']

            tags = set()
            for tag in tags_cleaned.split():
                tags.add(tag)
            data = data.read()
            replication = not replication and 25 or replication
            save = CLIENT.put(name, description, tags, 'django', 'django', 775, data, replication)
            form = UploadForm()
            return render_to_response(PUT_TEMPLATE,
                                        {'form_put': form.as_p(), 'save': save},
                                        context_instance=RequestContext(request))
    return render_to_response(PUT_TEMPLATE,
                                {'form_put': form.as_p()},
                                context_instance=RequestContext(request))