from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
Create your views here.
users/views.py
class CreateUserAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        user = request.data
        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @api_view(['POST'])
    @permission_classes([AllowAny, ])
    def authenticate_user(request):
        try:
            email = request.data['email']
            password = request.data['password']
            user = User.objects.get(email=email, password=password)
            if user:
                try:
                    payload = jwt_payload_handler(user)
                    token = jwt.encode(payload, settings.SECRET_KEY)
                    user_details = {}
                    user_details['name'] = "%s : %s" % (
                        user.login, user.email)
                    user_details['token'] = token
                    user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
                    return Response(user_details, status=status.HTTP_200_OK)
 
                except Exception as e:
                    raise e
            else:
                res = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                return Response(res, status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            res = {'error': 'please provide a email and a password'}
            return Response(res)