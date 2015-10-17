import os
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import  settings

# Create your views here.
def faceview(request):
    return render(request, 'faceapp/index.html')


def file_uploading_view(request):
    file = request.FILES.get('input_file', None)
    if not file:
        return HttpResponseBadRequest("No input file received")
    with open(os.path.join(settings.MEDIA_ROOT, file.name), 'wb') as out:
        for chunk in file.chunks():
            out.write(chunk)
    # TODO: return your model here
    return HttpResponse('Hello world!')