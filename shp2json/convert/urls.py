from django.conf.urls import url
from convert import views

urlpatterns = [
    url(r'^convertidor/$', views.datos_compuesto_list)
]