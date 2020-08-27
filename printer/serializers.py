from rest_framework import serializers
from .models import WorkUnit, ModelPrinter,ModelCartridge,ActPrinter, Producer,ActCartridge
from city.models import Cabinet
from city.serializers import CabinetSerializer
class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Producer
        fields=('id','name')
class ModelCartridgeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ModelCartridge
        fields=('id','name','count','reserved_count')
class ModelPrinterSerializer(serializers.ModelSerializer):
    producer=ProducerSerializer(read_only=True)
    cartridge=ModelCartridgeSerializer(read_only=True,many=True)
    class Meta:
        model=ModelPrinter
        fields=('id','name','producer','cartridge')

class WorkUnitSerializer(serializers.ModelSerializer):
    printer=ModelPrinterSerializer(read_only=True)
    cabinet=CabinetSerializer(read_only=True)
    class Meta:
        model=WorkUnit
        fields=('id','printer','color','status','status_note','cabinet','note','status_cartridge')
class ActPrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model=ActPrinter
        fields=('date','status','comment','printer')
class ActCartridgeSerializer(serializers.ModelSerializer):
    printer=WorkUnitSerializer(read_only=True)
    cartridge=ModelCartridgeSerializer(read_only=True)
    class Meta:
        model=ActCartridge
        fields=('id','date','status','cartridge','printer','date_finish')