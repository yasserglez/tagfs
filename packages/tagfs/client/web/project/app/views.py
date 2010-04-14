# -*- coding: utf-8 -*-

# Create your views here.

from django.conf.settings import TAGFSCLIENT as client

from forms import UploadForm

HOME_TEMPLATE = 'site/home.html'

def home(request):
	return render_to_response(HOME_TEMPLATE, 
								context_instance=RequestContext(request))


def upload_file(request):
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
            tags = form.cleaned_data['tags']
            data = form.cleaned_data['data']
            replication = form.cleaned_data['replication']
            save = client.put(name, description, tags, data, replication)
            form = UploadForm()
            return render_to_response(HOME_TEMPLATE, 
                                        {'form_upload': form, 'save': save},
                                        context_instance=RequestContext(request))
    else:        
        return render_to_response(HOME_TEMPLATE, 
                                    {'form_upload': form},
                                    context_instance=RequestContext(request))