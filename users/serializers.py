# users/serializers.py
from rest_framework import serializers
from.models import User

 
class UserSerializer(serializers.ModelSerializer):
 
    
    
    class Meta(object):
        model = User
        fields = ('id', 'name', 'city')
        # extra_kwargs = {'password': {'write_only': True}}
