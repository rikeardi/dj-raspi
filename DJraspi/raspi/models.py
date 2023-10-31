from typing import Any
import asyncio
import os
from pigpio_dht import DHT22
from django.db import models


# Create your models here.
class InvalidReadingError(Exception):
    def __str__(self) -> str:
        return super().__str__() + "Invalid reading"


class Pin(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=200)
    mode = models.CharField(max_length=200)
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name + ": " + str(self.number)


class Input(models.Model):
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    gpio = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=200)
    
    class Meta:
        abstract = True

    def __str__(self):
        return self.name + ": " + str(self.value)
    
    def id(self):
        return self.id


class OneWire(Input):
    pass


class Port(models.Model):
    pins = models.ManyToManyField(Pin)
    name = models.CharField(max_length=200)
    
    class Meta:
        abstract = True
    

class SerialPort(Port):
    # TX GPIO14, RX GPIO15
    pass


class I2CPort(Port):
    # SDA GPIO2, SCL GPIO3
    # EEPROM Data GPIO0, EEPROM Clock GPIO1
    pass


class SPIPort(Port):
    # SPI0: MOSI GPIO10, MISO GPIO9, SCLK GPIO11, CE0 GPIO8, CE1 GPIO7
    # SPI1: MOSI GPIO20, MISO GPIO19, SCLK GPIO21, CE0 GPIO18, CE1 GPIO17, CE2 GPIO16
    pass


class PWMPort(Port):
    # GPIO12, GPIO13, GPIO18, GPIO19
    pass


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


class RaspberryPi(models.Model):
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    pins = models.ManyToManyField(Pin)
    inputs = models.ManyToManyField(Input)
    ports = models.ManyToManyField(Port)
    sensors = models.ManyToManyField(Sensor)
    
    def fill(self):
        self.pins.add(Pin(number=1, name="3V3", mode="Power"))
        self.pins.add(Pin(number=2, name="5V", mode="Power"))
        self.pins.add(Pin(number=3, name="SDA", mode="I2C"))
        self.pins.add(Pin(number=4, name="5V", mode="Power"))
        self.pins.add(Pin(number=5, name="SCL", mode="I2C"))
        self.pins.add(Pin(number=6, name="Ground", mode="Power"))
        self.pins.add(Pin(number=7, name="GPIO4", mode="GPIO"))
        self.pins.add(Pin(number=8, name="TX", mode="Serial"))
        self.pins.add(Pin(number=9, name="Ground", mode="Power"))
        self.pins.add(Pin(number=10, name="RX", mode="Serial"))
        self.pins.add(Pin(number=11, name="GPIO17", mode="GPIO"))
        self.pins.add(Pin(number=12, name="GPIO18", mode="GPIO"))
        self.pins.add(Pin(number=13, name="GPIO27", mode="GPIO"))
        self.pins.add(Pin(number=14, name="Ground", mode="Power"))
        self.pins.add(Pin(number=15, name="GPIO22", mode="GPIO"))
        self.pins.add(Pin(number=16, name="GPIO23", mode="GPIO"))
        self.pins.add(Pin(number=17, name="3V3", mode="Power"))
        self.pins.add(Pin(number=18, name="GPIO24", mode="GPIO"))
        self.pins.add(Pin(number=19, name="GPIO10", mode="SPI"))
        self.pins.add(Pin(number=20, name="Ground", mode="Power"))
        self.pins.add(Pin(number=21, name="GPIO9", mode="SPI"))
        self.pins.add(Pin(number=22, name="GPIO25", mode="GPIO"))
        self.pins.add(Pin(number=23, name="GPIO11", mode="SPI"))
        self.pins.add(Pin(number=24, name="GPIO8", mode="SPI"))
        self.pins.add(Pin(number=25, name="Ground", mode="Power"))
        self.pins.add(Pin(number=26, name="GPIO7", mode="SPI"))
        self.pins.add(Pin(number=27, name="ID_SD", mode="I2C"))
        self.pins.add(Pin(number=28, name="ID_SC", mode="I2C"))
        self.pins.add(Pin(number=29, name="GPIO5", mode="GPIO"))
        self.pins.add(Pin(number=30, name="Ground", mode="Power"))
        self.pins.add(Pin(number=31, name="GPIO6", mode="GPIO"))
        self.pins.add(Pin(number=32, name="GPIO12", mode="GPIO"))
        self.pins.add(Pin(number=33, name="GPIO13", mode="GPIO"))
        self.pins.add(Pin(number=34, name="Ground", mode="Power"))
        self.pins.add(Pin(number=35, name="GPIO19", mode="GPIO"))
        self.pins.add(Pin(number=36, name="GPIO16", mode="GPIO"))
        self.pins.add(Pin(number=37, name="GPIO26", mode="GPIO"))
        self.pins.add(Pin(number=38, name="GPIO20", mode="GPIO"))
        self.pins.add(Pin(number=39, name="Ground", mode="Power"))
        self.pins.add(Pin(number=40, name="GPIO21", mode="GPIO"))

    def __str__(self):
        return self.name
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fill()
