# -*- coding: utf-8 -*-

# Create your views here.

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from forms import UploadForm, ListForm, SearchForm

HOME_TEMPLATE = 'site/home.html'
ALL_TAGS_TEMPLATE = 'site/all_tags.html'
LIST_TEMPLATE = 'site/list.html'
SEARCH_TEMPLATE = 'site/search.html'
PUT_TEMPLATE = 'site/put.html'
FILE_INFO_TEMPLATE = 'site/file_info.html'

CLIENT =  settings.TAGFSCLIENT

def home(request):
    return render_to_response(HOME_TEMPLATE,
                                context_instance=RequestContext(request))


def all_tags(request):
    """
    Muestra todos los tags del sistema.
    """
    return render_to_response(ALL_TAGS_TEMPLATE,
                                { 'tags': CLIENT.get_all_tags() },
                                context_instance=RequestContext(request))


def list_tags(request):
    """
    Lista los archivos que continen los tags recibidos por el get.
    """
    get_tags = request.GET.get('tags', '')
    tags = set()
    for tag in get_tags.split():
        tags.add(tag)
    form = ListForm({'tags': get_tags})
    return render_to_response(LIST_TEMPLATE,
                                { 'form_list': form, 'files': CLIENT.list(tags), 'active_tags': tags },
                                context_instance=RequestContext(request))


def search(request):
    """
    Lista los ficheros que contienen el texto search en el nombre,
    descripcion y tags.
    """
    search = request.GET.get('search', '')
    form = SearchForm({'search': search})
    return render_to_response(SEARCH_TEMPLATE,
                                { 'form_search': form, 'files': CLIENT.search(search) },
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


def file_info(request, file_hash):
    """
    Muestra todos los datos del fichero.
    """
    return render_to_response(FILE_INFO_TEMPLATE,
                                {'file_info': CLIENT.info(file_hash)},
                                context_instance=RequestContext(request))


def get(request, file_hash):
    """
    Devuelve el fichero para descargar.
    """
    return HttpResponse(CLIENT.get(file_hash), content_type='plain/text')