from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveDestroyAPIView, UpdateAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Subquery
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import filters
from rest_framework import status
from city.models import Cabinet
from users.models import User
from printer.models import WorkUnit, ModelCartridge,ActPrinter,ModelPrinter,ActCartridge
from .serializers import WorkUnitSerializer,ModelCartridgeSerializer,ModelPrinterSerializer ,ActPrinterSerializer,ActCartridgeSerializer
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
from telegram import telegram
from email_sender import email_sender
import datetime

# Create your views here.

#получаем принтеры в районе, который запрашиваем с фильтрами
class WorkUnitView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    filter_backends=(DjangoFilterBackend,filters.OrderingFilter)
    pagination_class=LimitOffsetPagination
    filterset_fields=('status',)
    ordering=('-id')
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
        printer_serializer=WorkUnitSerializer(unit,data={"status":3,"status_note":comment},partial=True)
        if serializer.is_valid() and printer_serializer.is_valid():
            serializer.save()
            printer_serializer.save()
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса принтера','Принтер ' + unit.printer.name + 'id:' + str(unit.id) + 'принят в диагностику' ,unit.cabinet.city.email_city)
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
            sender.send_mail_on_adress('Изменение статуса принтера','Принтер ' + unit.printer.name + 'id:' + str(unit.id) + 'отправлен в ремонт' ,unit.cabinet.city.email_city)
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
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса принтера','Принтер ' + unit.printer.name + 'id:' + str(unit.id) + 'готов и ожидает в ОГУПе' ,unit.cabinet.city.email_city)
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
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса принтера','Принтер ' + unit.printer.name + 'id:' + str(unit.id) + 'готов и ожидает в ОГУПе' ,unit.cabinet.city.email_city)
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
        comment=request.data.get('comment',"В работе")
        cabinet_id=request.data.get('cabinet')
        act=ActPrinter(status=1)
        unit = get_object_or_404(WorkUnit,id=printer_id)
        cabinet=get_object_or_404(Cabinet,id=cabinet_id)
        prevcab=unit.cabinet.city.name+" - "+unit.cabinet.name+" "
        unit.cabinet=cabinet
        act.comment="Перемещение принтера из "+ prevcab +"в - "+unit.cabinet.city.name+" - "+unit.cabinet.name+". "+comment
        serializer=ActPrinterSerializer(act,data={"printer":printer_id})
        printer_serializer=WorkUnitSerializer(unit,data={"status":1,"status_note":comment},partial=True)
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


##просмотр доступных картриджей

##заказ картриджа в комплексе
class OrderCartridgeView(ListCreateAPIView):
    permission_classes=[IsAuthenticated,]
    queryset=ActPrinter.objects.all()
    def create(self,request,*args,**kwargs):
        unit=get_object_or_404(WorkUnit,id=request.data.get('printer'))
        # import pdb;pdb.set_trace()
        cartridges=unit.printer.cartridge.all()
        unit.status_cartridge=False
        unit.save()
        for cartridge in cartridges:
            if cartridge.count!=0:
                cartridge.count-=1
                cartridge.reserved_count+=1
                cartridge.save()
                act=ActCartridge()
                act.cartridge=cartridge
                act.printer=unit
                act.save()
                text= '*Поcтупление новой заявки на картридж* \n\n'+act.cartridge.name+ '\n\n_Район:_ '+act.printer.cabinet.city.name + '\n\n_Данный картридж забронирован_'
                telegram.send(text)
                sender=email_sender()
                sender.send_mail_on_adress('Заказ на картридж от '+str(act.date) + ' принят в работу.','Картридж ' + act.cartridge.name +' для вашего района отправлен на заправку.',act.printer.cabinet.city.email_city)
                return Response({"results":"Картридж заказан"},status=status.HTTP_201_CREATED)
        act=ActCartridge()
        act.cartridge=cartridges.first()
        act.printer=unit
        act.status=1
        text= '*Поcтупление новой заявки на картридж*:\n\n'+act.cartridge.name+ '\n\n_Район:_ '+act.printer.cabinet.city.name + '\n\n _Необходимо отдать на заправку_'
        telegram.send(text)
        act.save()
        return Response({"results":"Картридж заказан"},status=status.HTTP_201_CREATED)

#просмотр информации о картриджах 
class CartridgePagination(LimitOffsetPagination):
    default_limit=20

class CartridgesListView(ListAPIView):
    permission_classes=[IsAuthenticated,]
    filter_backends=(DjangoFilterBackend,filters.OrderingFilter)
    ordering=('-id')
    pagination_class=CartridgePagination
    serializer_class=ModelCartridgeSerializer
    queryset=ModelCartridge.objects.all()

#передача заказа в заправку------------------------------------------------------------------------------------------------ 
class CartridgeRefill(APIView):
    permission_classes = (IsAuthenticated,) # explicit
    def patch(self, request):
        act_id = request.data.get('id')
        act=get_object_or_404(ActCartridge,id=act_id)
        serializer = ActCartridgeSerializer(act, data={"status":2},partial=True)
        if serializer.is_valid():
            serializer.save()
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса заказа на картридж '+str(act.id)+' от '+str(act.date),'Картридж ' + act.cartridge.name +'для вашего района отправлен на заправку.',act.printer.cabinet.city.email_city)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#принятие заказа из заправки ----------------------------------------------------------------------------------------------
class CartridgeComeback(APIView):
    permission_classes = (IsAuthenticated,) # explicit
    def patch(self, request):
        act_id = request.data.get('id')
        act=get_object_or_404(ActCartridge,id=act_id)
        act.cartridge.reserved_count+=1
        act.cartridge.save()
        serializer = ActCartridgeSerializer(act, data={"status":0},partial=True)
        if serializer.is_valid():
            serializer.save()
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса заказа на картридж '+str(act.id)+' от '+str(act.date),'Картридж ' + act.cartridge.name +' вернулся с заправки и ожидает.',act.printer.cabinet.city.email_city)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#закрытие заказа 
class CartridgeClose(APIView):
    permission_classes = (IsAuthenticated,) # explicit
    def patch(self, request):
        act_id = request.data.get('id')
        act=get_object_or_404(ActCartridge,id=act_id)
        act.cartridge.reserved_count-=1
        act.cartridge.save()
        act.printer.status_cartridge=True
        act.printer.save()
        act.date_finish=datetime.date.today()
        serializer = ActCartridgeSerializer(act, data={"status":4},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#отмена заказа
class CartridgeCancel(RetrieveDestroyAPIView):
    permission_classes=(IsAuthenticated,)
    def destroy(self,request):
        act_id=request.data.get('id')
        act=get_object_or_404(ActCartridge,id=act_id)
        if act.status==0:
            act.cartridge.reserved_count-=1
            act.cartridge.count+=1
            act.cartridge.save()
            act.printer.status_cartridge=True
            act.printer.save()
            act.delete()
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса заказа на картридж '+str(act_id)+' от '+str(act.date),'Заказ на картридж ' + act.cartridge.name +' отклонен администратором.',act.printer.cabinet.city.email_city)
        else:
            act.delete()
        return Response({"results":"Заказ отменен администратором"},status=status.HTTP_200_OK)
#принять все из заправки, что были отданы разом
class CartridgeComebackAll(APIView):
    permission_classes = (IsAuthenticated,) # explicit
    def patch(self, request):
        act_ids_not=request.data.get('ids',False)
        acts=ActCartridge.objects.filter(status=2)
        acts_for_edit=None
        if act_ids_not!=False:
            acts_subquery=ActCartridge.objects.filter(id__in=act_ids_not)
            acts_for_edit=acts.difference(acts_subquery)
        else: 
            acts_for_edit=acts
        for act in acts_for_edit:
            try:
                act.status=0
                
                act.cartridge.reserved_count+=1
                act.cartridge.save()
                act.save()
                sender=email_sender()
                sender.send_mail_on_adress('Изменение статуса заказа на картридж '+str(act.id)+' от '+str(act.date),'Картридж ' + act.cartridge.name +'для вашего района ожидает в ОГУПе.',act.printer.cabinet.city.email_city)
            except:
                return Response({'message':'Ошибка.'},status=status.HTTP_400_BAD_REQUEST)
        return Response({"results":"Заказ отменен администратором"},status=status.HTTP_200_OK)
#просмотр комплексом своих заказов/либо админом
class CartridgeActsView(ListAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class=ActCartridgeSerializer
    filter_backends=(DjangoFilterBackend,filters.OrderingFilter)
    pagination_class=LimitOffsetPagination
    search_fields=('id',)
    filterset_fields=('status','id')
    ordering=('-id')
    def get(self,request):
        city_id=request.query_params.get('city',request.user.city.id)
        if city_id=='0':
            acts=ActCartridge.objects.all()
        else:
            cabinets=Cabinet.objects.all().filter(city_id=city_id)
            printers=WorkUnit.objects.all().filter(cabinet_id__in=Subquery(cabinets.values('id')))
            acts=ActCartridge.objects.all().filter(printer_id__in=Subquery(printers.values('id')))
        queryset=self.filter_queryset(acts)
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer=self.serializer_class(page,many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=self.serializer_class(queryset,many=True)
        return Response({"results":serializer.data},status=status.HTTP_200_OK)
#выборка не заправленных админом
class CartridgeActsViewAdmin(ListAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class=ActCartridgeSerializer
    pagination_class=LimitOffsetPagination
    ordering=('-id')
    def get(self,request):
        acts=ActCartridge.objects.all().filter(status=1)
        queryset=self.filter_queryset(acts)
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer=self.serializer_class(page,many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=self.serializer_class(queryset,many=True)
        return Response({"results":serializer.data},status=status.HTTP_200_OK)
#выборка для принятия из заправки
class CartridgeActsViewAdmin2(ListAPIView):
    permission_classes=(IsAuthenticated,)
    serializer_class=ActCartridgeSerializer
    pagination_class=LimitOffsetPagination
    ordering=('-id')
    def get(self,request):
        acts=ActCartridge.objects.all().filter(status=2)
        queryset=self.filter_queryset(acts)
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer=self.serializer_class(page,many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer=self.serializer_class(queryset,many=True)
        return Response({"results":serializer.data},status=status.HTTP_200_OK)
#отправка выбранных на заправку (ids-массив исключений) -  - - - - - - - - - - - - -- - - - - - - - -  --  test
class CartridgeRefillAll(APIView):
    permission_classes = (IsAuthenticated,) # explicit
    def patch(self, request):
        act_ids_not=request.data.get('ids',False)
        acts=ActCartridge.objects.filter(status=1)
        acts_for_edit=None
        if act_ids_not!=False:
            acts_subquery=ActCartridge.objects.filter(id__in=act_ids_not)
            acts_for_edit=acts.difference(acts_subquery)
        else: 
            acts_for_edit=acts
        for act in acts_for_edit:
            try:
                act.status=2
                act.save()
                sender=email_sender()
                sender.send_mail_on_adress('Изменение статуса заказа на картридж '+str(act.id)+' от '+str(act.date),'Картридж ' + act.cartridge.name +'для вашего района отправлен на заправку.',act.printer.cabinet.city.email_city)
            except:
                return Response({'message':'Ошибка.'},status=status.HTTP_400_BAD_REQUEST)
        return Response({"results":"Картриджи отправлены в заправку"},status=status.HTTP_200_OK)

#редактирование статуса картриджда вручную
class ActEditStatus(APIView):
    permission_classes=(IsAuthenticated,)
    def patch(self,request):
        act_id=request.data.get('id')
        new_status=request.data.get('status')
        act=get_object_or_404(ActCartridge,id=act_id)
        serializer=ActCartridgeSerializer(act,data={"status":new_status},partial=True)
        if serializer.is_valid():
            serializer.save()
            sender=email_sender()
            sender.send_mail_on_adress('Изменение статуса заказа на картридж '+str(act.id)+' от '+str(act.date),'Картридж ' + act.cartridge.name +'для вашего района изменил статус.',act.printer.cabinet.city.email_city)
            return Response(serializer.data)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#редактирование таблицы картриджей
class CartridgeTableEdit(APIView):
    permission_classes=(IsAuthenticated,)
    def patch(self,request):
        cartridge_id=request.data.get('id')
        cartridge=get_object_or_404(ModelCartridge,id=cartridge_id)
        serializer=ModelCartridgeSerializer(cartridge,data={'count':request.data.get('count'),'reserved_count':request.data.get('reserved_count')},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


