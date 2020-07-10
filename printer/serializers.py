from rest_framework import serializers
from .models import WorkUnit, ModelPrinter,ModelCartridge,ActPrinter, Producer
from city.models import Cabinet
from city.serializers import CabinetSerializer
class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Producer
        fields=('id','name')
class ModelPrinterSerializer(serializers.ModelSerializer):
    producer=ProducerSerializer(read_only=True)
    class Meta:
        model=ModelPrinter
        fields=('id','name','producer')
class ModelCartridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ModelCartridge
        fields=('id','name','count','printer')
class WorkUnitSerializer(serializers.ModelSerializer):
    printer=ModelPrinterSerializer(read_only=True)
    cabinet=CabinetSerializer(read_only=True)
    class Meta:
        model=WorkUnit
        fields=('id','printer','color','status','status_note','cabinet','note')
class ActPrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model=ActPrinter
        fields=('date','status','comment','printer')