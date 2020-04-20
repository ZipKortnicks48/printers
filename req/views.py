from django.shortcuts import render
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveDestroyAPIView
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

#API района!

#просмотр заявок комплекса и добавление

class ReqView(ListCreateAPIView):
    serializer_class=ReqSerializer
    def get_queryset(self):#получаем заявки для района пользователя
        city_id=self.request.user.city.id
        cabinets=Cabinet.objects.all().filter(city_id=city_id)
        reqs=Req.objects.all().filter(cabinet_id__in=Subquery(cabinets.values('id')))
        return reqs
    def create(self, request, *args, **kwargs):
        # import pdb; pdb.set_trace() 
        req = Req(user=self.request.user)
        serializer = self.serializer_class(req,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request):#публикуем заявки для района пользователя 
        queryset = self.get_queryset()
        filter_backends = [filters.SearchFilter,DjangoFilterBackend]
        search_fields = ['shortname','id']
        filterset_fields = ['date', 'cabinet','status']
        ordering_fields=['date','status','checkout']
        serializer = ReqSerializer(queryset, many=True)
        return Response(serializer.data)
    
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
        # import pdb; pdb.set_trace() 
        req=self.request.query_params.get('req')
        comments=Comment.objects.all().filter(req=req)
        return comments
    def create(self, request, *args, **kwargs):
        import pdb; pdb.set_trace() 
        req=request.query_params.get('req')
        req=Req.objects.all().filter(id=req)
        comment = Comment(user=self.request.user,req=req)
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
    

    