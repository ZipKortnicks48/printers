# users/serializers.py
from rest_framework import serializers
from.models import User

 
class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ('id', 'password','name', 'city','phone','mobile_phone','surname')
        # extra_kwargs = {'password': {'write_only': True}}
