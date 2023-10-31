from typing import Any
import asyncio
import os
from pigpio_dht import DHT22
from django.db import models


# Create your models here.
class InvalidReadingError(Exception):
    def __str__(self) -> str:
        return super().__str__() + "Invalid reading"


class Input(models.Model):
    gpio = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=200)
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.name + ": " + str(self.value)
    
    def id(self):
        return self.id


class OneWire(Input):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Sensor(models.Model):
    name = models.CharField(max_length=200)
    values = models.ManyToManyField('SensorValue')
    sensor = Any
    type = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name

    def read():
        pass


class Reading(models.Model):
    value = Any
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.value) + " @ " + str(self.timestamp)


class SensorValue(models.Model):
    name = models.CharField(max_length=200)
    type = Any
    readings = models.ManyToManyField('Reading')
    
    def __str__(self):
        return self.name
        

class DHT22(Sensor):
    sensor = None
    input = models.ForeignKey(OneWire, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "DHT22"
        verbose_name_plural = "DHT22s"
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.sensor = DHT22(self.input.gpio)
        self.values = [
            SensorValue(name="Temperature", type=float),
            SensorValue(name="Humidity", type=float)
        ]
        super().__init__(*args, **kwargs)
    
    def read(self):
        try:
            result = self.sensor.read()
            if result['valid']:
                self.values[0].readings.add(Reading(value=result['temp_c']))
                self.values[1].readings.add(Reading(value=result['humidity']))
            else:
                raise InvalidReadingError
        except Exception as e:
            pass
    
    def start():
        pass
