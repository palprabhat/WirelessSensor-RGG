from django.conf.urls import url

from plot import views

urlpatterns = [
    url(r'^plot', views.plot_graph),
    url(r'^$', views.plot_graph),
]