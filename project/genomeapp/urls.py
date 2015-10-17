from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'genomeapp.views.index', name='index'),
]
