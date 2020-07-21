from .models import Cabinet, City
from rest_framework import serializers

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model=City
        fields='__all__'
class CabinetSerializer(serializers.ModelSerializer):
    city=CitySerializer(read_only=True)
    class Meta:
        model=Cabinet
        fields=('id','number','name','city')
        # read_only_fields=('city',)