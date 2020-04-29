from .models import Req
from users.serializers import UserSerializer
from rest_framework import serializers

class ReqSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model=Req
        fields=('id','shortname','description','date','deadline','cabinet','user','status','checkout','finishdate')
class CommentSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    req=ReqSerializer(read_only=True)
    class Meta:
        model=Req
        fields=('id','date','user','text','req')