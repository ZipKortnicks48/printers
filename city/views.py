from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CabinetSerializer
from .models import Cabinet
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
# Create your views here.

class CabinetView(ListAPIView):
    permission_classes = [AllowAny] #стереть для защиты
    serializer_class=CabinetSerializer
    def get_queryset(self):
        city_id=self.request.user.city.id
        cabinets=Cabinet.objects.all().filter(city_id=city_id)
        return cabinets
    def list(self, request):
        queryset = self.get_queryset()
        serializer = CabinetSerializer(queryset, many=True)
        return Response(serializer.data)