from rest_framework import serializers
from .models import *


class DHT22Serializer(serializers.ModelSerializer):
    class Meta:
        model = DHT22
        fields = '__all__'