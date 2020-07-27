from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveDestroyAPIView, UpdateAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Subquery
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from city.models import Cabinet
from users.models import User
from printer.models import WorkUnit, ModelCartridge,ActPrinter,ModelPrinter
from .serializers import WorkUnitSerializer,ModelCartridgeSerializer,ModelPrinterSerializer ,ActPrinterSerializer
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from telegram import telegram
from email_sender import email_sender
# Create your views here.

#получаем принтеры в районе, который запрашиваем с фильтрами
class WorkUnitView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    filter_backends=(DjangoFilterBackend,)
    pagination_class=LimitOffsetPagination
    filterset_fields=('status',)
    serializer_class=WorkUnitSerializer
    def get_queryset(self):
        workunits=WorkUnit.objects.all()
        city_id=self.request.query_params.get('city',self.request.user.city.id)
        printer_searchword=self.request.query_params.get('printer','')
        if city_id!='0':
            cabinets=Cabinet.objects.all().filter(city_id=city_id)
            workunits=workunits.filter(cabinet_id__in=Subquery(cabinets.values('id')))
        if printer_searchword!='':
            printer_models=ModelPrinter.objects.filter(name__icontains=printer_searchword)
            workunits_withprinters=workunits.filter(printer_id__in=Subquery(printer_models.values('id')))
            workunits_withids=workunits.filter(id=printer_searchword)
            workunits=workunits_withprinters|workunits_withids
        return workunits
    def list(self,request):
        queryset=self.filter_queryset(self.get_queryset())
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer=self.serializer_class(page,many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=self.serializer_class(queryset,many=True)
            return Response(serializer.data)    
#получить картриджи по модели принтера
class ModelCartridgeView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=ModelCartridgeSerializer
    def get_queryset(self):
        printer_id=self.request.query_params.get('printer',None)
        cartridges=ModelCartridge.objects.all().filter(printer_id=printer_id)
        return cartridges
    def list(self,request):
        queryset=self.get_queryset()
        serializer=self.serializer_class(queryset,many=True)
        return Response(serializer.data) 
#отправка комментария о поломке из комплекса
class BrokeView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        city=request.user.city.name
        comment=request.data.get('comment')
        printer_id=request.data.get('printer')
        act=ActPrinter(status=2)
        serializer=ActPrinterSerializer(act,data=request.data)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        printer_serializer=WorkUnitSerializer(unit,data={"status":2,"status_note":comment},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            text='*Поломка принтера* id:'+request.data['printer']+'\n\n'+unit.printer.name+'\n\n_Причина_: '+comment+ '\n\n_Район:_ '+city
            telegram.send(text)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#перевод в диагностику
class DiagnosticView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        printer_id=request.data.get('printer')
        unit = get_object_or_404(WorkUnit,id=printer_id)
        comment=request.data.get('comment',unit.status_note)
        act=ActPrinter(status=3)
        act.comment=comment
        serializer=ActPrinterSerializer(act,data=request.data)
        printer_serializer=WorkUnitSerializer(unit,data={"status":3,"comment":comment},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#отправка в ремонт
class ServView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        comment=request.data.get('comment')
        printer_id=request.data.get('printer')
        act=ActPrinter(status=4)
        act.comment=comment
        serializer=ActPrinterSerializer(act,data=request.data)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        printer_serializer=WorkUnitSerializer(unit,data={"status":4,"status_note":comment},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            text='Добрый день!\n\nВышел из строя принтер '+unit.printer.name+'.\n\nПричина: '+comment
            sender=email_sender()
            sender.send_email(text)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#забрали из ремонта
class WaitingView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        printer_id=request.data.get('printer')
        act=ActPrinter(status=5)
        act.comment="Прибытие из ремонта"
        serializer=ActPrinterSerializer(act,data=request.data)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        printer_serializer=WorkUnitSerializer(unit,data={"status":5,"status_note":"Принтер прибыл с ремонта и ожидает в ИТ-отделе."},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#неполадки устранены своими силами
class ServUsView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        printer_id=request.data.get('printer')
        act=ActPrinter(status=6)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        act.comment="Устранено своими силами - "+request.data.get('comment',unit.status_note)
        serializer=ActPrinterSerializer(act,data=request.data)
        printer_serializer=WorkUnitSerializer(unit,data={"status":5,"status_note":"Принтер починен и ожидает в ИТ-отделе."},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#возвращение принтера в комплекс после ремонта, выдача
class RetView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        printer_id=request.data.get('printer')
        act=ActPrinter(status=1)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        act.comment="Возвращение принтера после ремонта в "+unit.cabinet.city.name+". "+request.data.get('comment')
        serializer=ActPrinterSerializer(act,data={"printer":printer_id})
        printer_serializer=WorkUnitSerializer(unit,data={"status":1,"status_note":"В работе"},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#перемещение принтера в другой район/кабинет
class MoveView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        printer_id=request.data.get('printer')
        comment=request.data.get('comment',"")
        cabinet_id=request.data.get('cabinet')
        act=ActPrinter(status=1)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        cabinet=get_object_or_404(Cabinet,id=cabinet_id)
        prevcab=unit.cabinet.city.name+" - "+unit.cabinet.name+" "
        unit.cabinet=cabinet
        act.comment="Перемещение принтера из "+ prevcab +"в - "+unit.cabinet.city.name+" - "+unit.cabinet.name+". "+comment
        serializer=ActPrinterSerializer(act,data={"printer":printer_id})
        printer_serializer=WorkUnitSerializer(unit,data={"status":1,"status_note":"В работе"},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#списание принтера
class DeleteView(ListCreateAPIView):
    permission_classes=[IsAdminUser,]
    queryset=ActPrinter.objects.all()
    def create(self, request, *args, **kwargs):
        printer_id=request.data.get('printer')
        unit = get_object_or_404(WorkUnit,id=printer_id)
        comment=request.data.get('comment',unit.status_note)
        act=ActPrinter(status=7)
        act.comment=comment
        serializer=ActPrinterSerializer(act,data=request.data)
        printer_serializer=WorkUnitSerializer(unit,data={"status":6,"comment":comment},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)