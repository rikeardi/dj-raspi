from collections.abc import Iterable
from typing import Any
import asyncio
import os
from django.db import models
from single_instance_model import SingleInstanceModel

from pigpio_dht import DHT22
import Adafruit_BMP.BMP085 as dht_bmp


# Create your models here.
class InvalidReadingError(Exception):
    def __str__(self) -> str:
        return super().__str__() + "Invalid reading"


class Pin(models.Model):
    number = models.IntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=200)
    mode = models.CharField(max_length=200)
    used = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.number) + ": " + self.name + " (" + self.mode + ")"


class Input(models.Model):
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE, null=True)
    gpio = models.IntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pin.mode == "GPIO":
            self.gpio = self.pin.name.split("GPIO")[1]
        super().save(*args, **kwargs)


class OneWire(Input):
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE, null=True, limit_choices_to={'mode': 'GPIO'})
    
    class Meta:
        verbose_name = "OneWire"
        verbose_name_plural = "OneWires"
    
    def __str__(self) -> str:
        return "OneWire: GPIO" + str(self.gpio)


class Port(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.name
    

class SerialPort(Port):
    tx = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="tx", limit_choices_to={'mode': 'GPIO'})
    rx = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="rx", limit_choices_to={'mode': 'GPIO'})
    port_ptr = models.OneToOneField(Port, blank=True, default=None, on_delete=models.DO_NOTHING, parent_link=True)
    Port._meta.get_field('type').default = "Serial"
    # TX GPIO14, RX GPIO15
    
    class Meta:
        verbose_name = "Serial Port"
        verbose_name_plural = "Serial Ports"


class I2CPort(Port):
    sda = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="sda", limit_choices_to={'mode': 'GPIO'})
    scl = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="scl", limit_choices_to={'mode': 'GPIO'})
    port_ptr = models.OneToOneField(Port, blank=True, default=None, on_delete=models.DO_NOTHING, parent_link=True)
    Port._meta.get_field('type').default = "I2C"
    # SDA GPIO2, SCL GPIO3
    # EEPROM Data GPIO0, EEPROM Clock GPIO1
    
    class Meta:
        verbose_name = "I2C Port"
        verbose_name_plural = "I2C Ports"


class SPIPort(Port):
    mosi = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="mosi", limit_choices_to={'mode': 'GPIO'})
    miso = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="miso", limit_choices_to={'mode': 'GPIO'})
    sclk = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="sclk", limit_choices_to={'mode': 'GPIO'})
    ce0 = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="ce0", limit_choices_to={'mode': 'GPIO'}, null=True, blank=True)
    ce1 = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="ce1", limit_choices_to={'mode': 'GPIO'}, null=True, blank=True)
    ce2 = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name="ce2", limit_choices_to={'mode': 'GPIO'}, null=True, blank=True)
    port_ptr = models.OneToOneField(Port, blank=True, default=None, on_delete=models.DO_NOTHING, parent_link=True)
    Port._meta.get_field('type').default = "SPI"
    # SPI0: MOSI GPIO10, MISO GPIO9, SCLK GPIO11, CE0 GPIO8, CE1 GPIO7
    # SPI1: MOSI GPIO20, MISO GPIO19, SCLK GPIO21, CE0 GPIO18, CE1 GPIO17, CE2 GPIO16
    
    class Meta:
        verbose_name = "SPI Port"
        verbose_name_plural = "SPI Ports"


class PWMPort(Port):
    pin = models.ForeignKey(Pin, limit_choices_to={'mode': 'GPIO'}, on_delete=models.CASCADE, related_name="pin")
    port_ptr = models.OneToOneField(Port, blank=True, default=None, on_delete=models.DO_NOTHING, parent_link=True)
    Port._meta.get_field('type').default = "PWM"
    # GPIO12, GPIO13, GPIO18, GPIO19
    
    class Meta:
        verbose_name = "PWM Port"
        verbose_name_plural = "PWM Ports"


class Reading(models.Model):
    reading = Any
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        #abstract = True
    
    def __str__(self):
        return str(self.reading) + " @ " + str(self.timestamp)


class SensorValue(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200, default="float")
    unit = models.CharField(max_length=200, blank=True, null=True)
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, blank=True, null=True)
    reading = models.ForeignKey('Reading', on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.name


class Sensor(models.Model):
    name = models.CharField(max_length=200)
    sensor = None
    type = models.CharField(max_length=200, blank=True, null=True)
    values = models.ManyToManyField(Reading, through=SensorValue)
    interval = models.IntegerField(default=60)

    #class Meta:
        #abstract = True
    
    def __str__(self):
        return self.name

    def read():
        pass
        

class DHT22(Sensor):
    input = models.ForeignKey(OneWire, on_delete=models.CASCADE)
    sensor_ptr = models.OneToOneField(Sensor, blank=True, default=None, on_delete=models.DO_NOTHING, parent_link=True)
    Sensor._meta.get_field('type').default = "DHT22"
    
    class Meta:
        verbose_name = "DHT22"
        verbose_name_plural = "DHT22s"
    
    async def read(self):
        try:
            result = self.sensor.read()
            if result['valid']:
                self.values.add(SensorValue(name='Temperature', type='float', unit='°C', sensor=self, reading=Reading(reading=result['temp'])).save())
                self.values.add(SensorValue(name='Humidity', type='float', unit='%', sensor=self, reading=Reading(reading=result['humidity'])).save())
                self.save()
            else:
                raise InvalidReadingError
        except Exception as e:
            pass
    
    def start(self):
        self.sensor = DHT22(self.input.gpio)
        while True:
            asyncio.run(self.read())
            asyncio.sleep(self.interval)


class BMP085(Sensor):
    port = models.ForeignKey(I2CPort, on_delete=models.CASCADE)
    address = models.IntegerField(default=0x77)
    sensor_ptr = models.OneToOneField(Sensor, blank=True, default=None, on_delete=models.DO_NOTHING, parent_link=True)
    Sensor._meta.get_field('type').default = "BMP085"
    
    class Meta:
        verbose_name = "BMP085"
        verbose_name_plural = "BMP085s"
    
    async def read(self):
        try:
            result = self.sensor.read()
            if result['valid']:
                self.values.add(SensorValue(name='Temperature', type='float', unit='°C', sensor=self, reading=Reading(reading=result['temp'])).save())
                self.values.add(SensorValue(name='Pressure', type='float', unit='hPa', sensor=self, reading=Reading(reading=result['pressure'])).save())
                self.values.add(SensorValue(name='Altitude', type='float', unit='m', sensor=self, reading=Reading(reading=result['altitude'])).save())
                self.save()
            else:
                raise InvalidReadingError
        except Exception as e:
            pass
    
    def start(self):
        self.sensor = dht_bmp.BMP085(address=self.address, busnum=self.port.name.split("I2C-")[1])
        while True:
            asyncio.run(self.read())
            asyncio.sleep(self.interval)


class SingletonModel(models.Model):
    
    class Meta:
        abstract = True
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        print(cls)
        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class RaspberryPi(SingletonModel):
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    pins = models.ManyToManyField(Pin)
    ports = models.ManyToManyField(SerialPort)
    
    class Meta:
        verbose_name = "Raspberry Pi"
        verbose_name_plural = "Raspberry Pi"
            
    def fill(self):
        _pins = (
            (1, "3V3", "Power"),
            (2, "5V", "Power"),
            (3, "GPIO2", "GPIO"),
            (4, "5V", "Power"),
            (5, "GPIO3", "GPIO"),
            (6, "GND", "Ground"),
            (7, "GPIO4", "GPIO"),
            (8, "GPIO14", "GPIO"),
            (9, "GND", "Ground"),
            (10, "GPIO15", "GPIO"),
            (11, "GPIO17", "GPIO"),
            (12, "GPIO18", "GPIO"),
            (13, "GPIO27", "GPIO"),
            (14, "GND", "Ground"),
            (15, "GPIO22", "GPIO"),
            (16, "GPIO23", "GPIO"),
            (17, "3V3", "Power"),
            (18, "GPIO24", "GPIO"),
            (19, "GPIO10", "GPIO"),
            (20, "GND", "Ground"),
            (21, "GPIO9", "GPIO"),
            (22, "GPIO25", "GPIO"),
            (23, "GPIO11", "GPIO"),
            (24, "GPIO8", "GPIO"),
            (25, "GND", "Ground"),
            (26, "GPIO7", "GPIO"),
            (27, "GPIO0", "GPIO"),
            (28, "GPIO1", "GPIO"),
            (29, "GPIO5", "GPIO"),
            (30, "GND", "Ground"),
            (31, "GPIO6", "GPIO"),
            (32, "GPIO12", "GPIO"),
            (33, "GPIO13", "GPIO"),
            (34, "GND", "Ground"),
            (35, "GPIO19", "GPIO"),
            (36, "GPIO16", "GPIO"),
            (37, "GPIO26", "GPIO"),
            (38, "GPIO20", "GPIO"),
            (39, "GND", "Ground"),
            (40, "GPIO21", "GPIO")
        )
        for pin in _pins:
            self.pins.add(Pin(name=pin[1], number=pin[0], mode=pin[2]).save())
        
        _serialport = SerialPort(name="/dev/ttyS0", tx=Pin.objects.get(number=8),
                                 rx=Pin.objects.get(number=10)).save()
        self.ports.add(_serialport)
        
        _i2cport = I2CPort(name="I2C-1", sda=Pin.objects.get(number=3),
                           scl=Pin.objects.get(number=5)).save()
        self.ports.add(_i2cport)
        
        _i2cport = I2CPort(name="I2C-20", sda=Pin.objects.get(number=27),
                           scl=Pin.objects.get(number=28)).save()
        self.ports.add(_i2cport)
        
        _spiport = SPIPort(name="SPI0", mosi=Pin.objects.get(number=19),
                           miso=Pin.objects.get(number=21),
                           sclk=Pin.objects.get(number=23),
                           ce0=Pin.objects.get(number=24),
                           ce1=Pin.objects.get(number=26)).save()
        self.ports.add(_spiport)
        
        _spiport = SPIPort(name="SPI1", mosi=Pin.objects.get(number=38),
                           miso=Pin.objects.get(number=35),
                           sclk=Pin.objects.get(number=40),
                           ce0=Pin.objects.get(number=12),
                           ce1=Pin.objects.get(number=11),
                           ce2=Pin.objects.get(number=36)).save()
        self.ports.add(_spiport)
        
        _pwmport = PWMPort(name="PWM0", pin=Pin.objects.get(number=32)).save()
        self.ports.add(_pwmport)
        
        _pwmport = PWMPort(name="PWM1", pin=Pin.objects.get(number=33)).save()
        self.ports.add(_pwmport)
        
        _pwmport = PWMPort(name="PWM2", pin=Pin.objects.get(number=12)).save()
        self.ports.add(_pwmport)
        
        _pwmport = PWMPort(name="PWM3", pin=Pin.objects.get(number=35)).save()
        self.ports.add(_pwmport)
    
    def __str__(self):
        return self.name
