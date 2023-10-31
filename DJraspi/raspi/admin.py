from django.contrib import admin
from .models import *

admin.site.register(OneWire)
admin.site.register(Reading)
admin.site.register(SensorValue)
admin.site.register(DHT22)
