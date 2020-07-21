from .models import Req, Comment
from users.serializers import UserSerializer
from city.serializers import CabinetSerializer
from rest_framework import serializers

class ReqSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    executor=UserSerializer(read_only=True)
    cabinet=CabinetSerializer(read_only=True)
    class Meta:
        model=Req
        fields=('id','shortname','description','date','deadline','cabinet','user','status','checkout','finishdate','executor','phone')
class CommentSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    #req=ReqSerializer(read_only=True)
    class Meta:
        model=Comment
        fields=('id','date','user','text','req')