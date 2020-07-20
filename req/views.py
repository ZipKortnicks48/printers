from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveDestroyAPIView, UpdateAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Subquery
from .serializers import ReqSerializer, CommentSerializer
from .models import Req, Comment
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import status
from city.models import Cabinet
from users.models import User
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from django.db.models.query import QuerySet
import telebot

#API района!

#просмотр заявок комплекса и добавление

class ReqView(ListCreateAPIView):
    serializer_class=ReqSerializer
    filter_backends =(filters.SearchFilter,DjangoFilterBackend,filters.OrderingFilter)
    search_fields = ('shortname','id',)
    filterset_fields = ('date', 'cabinet')
    ordering=('-date')
    pagination_class=LimitOffsetPagination
    def get_queryset(self):#получаем заявки для района пользователя
        city_id=self.request.user.city.id
        cabinets=Cabinet.objects.all().filter(city_id=city_id)
        show_only_open=self.request.query_params.get('status',False)
        reqs=Req.objects.all().filter(cabinet_id__in=Subquery(cabinets.values('id')))
        if show_only_open:
            reqs=reqs.exclude(status="3")
        return reqs
    def create(self, request, *args, **kwargs):
        req = Req(user=self.request.user)
        serializer = self.serializer_class(req,data=request.data)
        if serializer.is_valid():
            serializer.save()
            TOKEN='1191171470:AAFD2RFpUR0-W_RTqO4uco2WpCAZOCT1b4M'
            bot=telebot.TeleBot(TOKEN)
            text='*Поступление новой заявки*\n\n'+request.data['shortname']+'\n\n_Автор:_ '+request.user.surname+'\n_Телефон:_ '+request.data['phone']
            bot.send_message('-488020289',text,parse_mode="Markdown")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request):#публикуем заявки для района пользователя 
        queryset = self.filter_queryset(self.get_queryset())
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReqSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReqSerializer(queryset, many=True)
        return Response(serializer.data)




#просмотр заявок админом
class ReqAdminView(ListAPIView):
    permission_classes=[IsAdminUser, ]
    serializer_class=ReqSerializer
    filter_backends =(filters.SearchFilter,
    #DjangoFilterBackend,
    filters.OrderingFilter)
    search_fields = ('shortname','id',)
    #filterset_fields = ('date','status','cabinet')
    ordering=('-date')
    pagination_class=LimitOffsetPagination
    def get_queryset(self):
        city_id=self.request.query_params.get('city',None)
        cabinet_id=self.request.query_params.get('cabinet',None)
        executor_id=self.request.query_params.get('executor',None)
        date_id=self.request.query_params.get('date',None)
        only_new=self.request.query_params.get('only_new',False)
        only_finished=self.request.query_params.get('only_finished',False)
        only_process=self.request.query_params.get('only_process',False)
        only_checkout=self.request.query_params.get('only_checkout',False)
        reqs=Req.objects.all()
        if city_id!=None:
            cabinets=Cabinet.objects.all().filter(city_id=city_id)
            reqs=reqs.filter(cabinet_id__in=Subquery(cabinets.values('id')))
        if cabinet_id!=None:
            reqs=reqs.filter(cabinet_id=cabinet_id)
        if executor_id!=None:
            reqs=reqs.filter(executor_id=executor_id)
        if only_checkout=='true':
            reqs=reqs.filter(checkout=True)
        if only_new or only_process or only_finished:              
            new_s=reqs.none()
            process_s=reqs.none()
            finished_s=reqs.none()
            # import pdb;pdb.set_trace()
            if only_new=='true':
                new_s=reqs.filter(status='1')
            if only_process=='true':
                process_s=reqs.filter(status='2') 
            if only_finished=='true':
                finished_s=reqs.filter(status='3')
            #reqs=set(new_s|process_s|finished_s)
            reqs=new_s|process_s|finished_s  
        return reqs
    def list(self, request):#публикуем заявки для района пользователя 
        queryset = self.filter_queryset(self.get_queryset())
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReqSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReqSerializer(queryset, many=True)
        return Response(serializer.data)

#назначение ответственного задаче

class ReqAppointView(APIView):
    permission_classes = (IsAdminUser,) # explicit
    def patch(self, request):
        req_id = request.data.get('id')
        req=get_object_or_404(Req,id=req_id)
        executor_id=request.data.get('executor')
        executor=get_object_or_404(User,id=executor_id)
        req.executor=executor
        req.status="2"
        serializer = ReqSerializer(req, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReqCloseView(APIView):
    permission_classes=(IsAdminUser,)
    def patch(self,request):
        req_id = request.data.get('id')
        req=get_object_or_404(Req,id=req_id)
        executor_id=request.data.get('executor')
        req.executor=request.user
        req.status="3"
        serializer = ReqSerializer(req, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
#просмотр заявки и удаление

class SingleReqView(RetrieveDestroyAPIView):#попытка удалить заявку пользователя
    queryset=Req.objects.all()
    serializer_class=ReqSerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cabinet=Cabinet.objects.get(id=instance.cabinet.id)
        city=cabinet.city.id
        if city==request.user.city.id:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class CommentView(ListCreateAPIView):
    serializer_class=CommentSerializer
    def get_queryset(self):#получаем комментарии к заявке
        req=self.request.query_params.get('req', None)
        comments=Comment.objects.all().filter(req=req)
        return comments
    def create(self, request, *args, **kwargs):
        req_id=request.data.get('req')
        req=Req.objects.all().filter(id=req_id).first()
        comment = Comment(user=self.request.user,req=req)
        TOKEN='1191171470:AAFD2RFpUR0-W_RTqO4uco2WpCAZOCT1b4M'
        bot=telebot.TeleBot(TOKEN)
        text='*Новый комментарий*\n\n'+request.data['text']+'\n\n_Автор:_ '+request.user.surname+'\n_Номер заявки:_ '+req_id
        bot.send_message('-488020289',text,parse_mode="Markdown")
        serializer = self.serializer_class(comment,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request):#публикуем список комментов
        queryset = self.get_queryset()
        ordering_fields=['date']
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)
    

    
