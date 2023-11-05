from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sensor/<str:type>/<int:id>/', views.sensor, name='sensor'),
    path('port/<str:type>/<int:id>/', views.port, name='port')
]