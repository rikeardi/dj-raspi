from django.contrib import admin
from .models import *
from single_instance_model.admin import SingleInstanceModelAdmin

@admin.register(RaspberryPi)
class RaspberryPiAdmin(SingleInstanceModelAdmin):
    pass

admin.site.register(Pin)
admin.site.register(OneWire)
admin.site.register(SensorValue)
admin.site.register(Sensor)
admin.site.register(SerialPort)
admin.site.register(I2CPort)
admin.site.register(SPIPort)
admin.site.register(PWMPort)