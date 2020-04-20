from django.shortcuts import render
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from users.serializers import UserSerializer
from rest_framework_jwt.settings import api_settings
import jwt
import printers.settings as settings
# class CreateUserAPIView(APIView):
#     permission_classes = (AllowAny,)
#     def post(self, request):
#         user = request.data
#         serializer = UserSerializer(data=user)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    # try:
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        name = request.data['name']
        # import pdb; pdb.set_trace()
        password = request.data['password']
        user = User.objects.get(name=name)
        if check_password(password,user.password):
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {}
                user_details['name'] = user.name
                user_details['token'] = token
                user_logged_in.send(sender=user.__class__, request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)
            except Exception as e:
                raise e
        else:
            res = {'error': 'Неверный пароль'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    # except:
    #     res = {'error': 'Проверьте правильность введенных данных.'}
    #     return Response(res, status=status.HTTP_400_BAD_REQUEST)


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url 
    permission_classes = (AllowAny,)
    def post(self, request):
        try:
            user = request.data
            serializer = UserSerializer(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            res={'error': 'Проверьте правильность введенных данных.'}
            return Response(res,status=status.HTTP_400_BAD_REQUEST)