import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from redactor.forms import ImageForm
from easy_thumbnails.files import get_thumbnailer

import json


UPLOAD_PATH = getattr(settings, 'REDACTOR_UPLOAD', 'redactor/')


@csrf_exempt
@require_POST
@user_passes_test(lambda u: u.is_staff)
def redactor_upload(request, upload_to=None, form_class=ImageForm,
                    response=lambda name, url: url):
    form = form_class(request.POST, request.FILES)
    
    if form.is_valid():
        file_ = form.cleaned_data['file']
        filename = "%s.%s" % (uuid.uuid4(), file_.name.split('.')[-1])
        path = os.path.join(upload_to or UPLOAD_PATH, filename)
        real_path = default_storage.save(path, file_)

        if form_class == ImageForm:
            redim = get_thumbnailer(real_path).get_thumbnail({'size': (400, 400), 'crop': "smart"}).url

            images = [{"filelink": redim, "file": real_path }]

            return HttpResponse( json.dumps(images), mimetype="application/json" )

            #return HttpResponse(
            #        response( redim,
            #                 redim)
            #    )
        else:
            files = [{'filelink': default_storage.url(real_path)}]
            
            return HttpResponse( json.dumps(files), mimetype="application/json" )
        
    return HttpResponse(status=403)
