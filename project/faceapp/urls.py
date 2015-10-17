from django.conf.urls import include, url
from faceapp import views

urlpatterns = [
    url(r'^$', views.faceview),
    url(r'^onupload$', views.file_uploading_view)
]
