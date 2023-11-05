import json
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import *
from .serializers import *


def index(request):
    raspi = get_object_or_404(RaspberryPi)
    sensors = Sensor.objects.all().select_related()
    dht22 = DHT22.objects.all().select_related()
    bmp085 = BMP085.objects.all().select_related()
    pins = raspi.pins.all()
    colors = {
        "Power": "red",
        "Ground": "black",
        "GPIO": "green",
    }
    context = {
        'raspi': raspi,
        'pins': pins,
        'sensors': sensors,
        'dht22': dht22,
        'bmp085': bmp085,
        'colors': colors,
    }
    return render(request, 'index.html', context)


def sensor(request, type, id):
    model = eval(type)
    sensor = get_object_or_404(model, id=id)
    context = {
        'sensor': sensor,
    }
    return render(request, sensor.type + '.html', context)


def port(request, type, id):
    model = eval(type)
    port = get_object_or_404(model, id=id)
    context = {
        'port': port,
    }
    return render(request, port.type + '.html', context)