from django.db import models
from city.models import Cabinet
from django.utils import timezone
from city.models import Cabinet
from users.models import User
import datetime

# Create your models here.

class Req(models.Model):
    shortname = models.CharField(max_length=255)
    description=models.TextField()
    date=models.DateField(default=datetime.date.today)
    deadline=models.DateField(blank=True,null=True)
    finishdate=models.DateField(blank=True,default=datetime.date.today)
    cabinet=models.ForeignKey(Cabinet,related_name="req_have_cabinet",on_delete=models.CASCADE)
    user=models.ForeignKey(User,related_name="req_have_user",on_delete=models.CASCADE)
    executor=models.ForeignKey(User,related_name="req_have_executor",on_delete=models.CASCADE,blank=True,null=True)
    status=models.CharField(max_length=1,default="1")
    checkout=models.BooleanField(default=False)
    phone=models.CharField(max_length=11,blank=True,null=True)
    def __str__(self):
        cabinet=Cabinet.objects.get(id=self.cabinet.id)
        return str(self.id)+". "+cabinet.__str__()+" - "+self.shortname

class Comment(models.Model):
    date=models.DateField(default=datetime.date.today)
    user=models.ForeignKey(User,related_name="comment_have_user",on_delete=models.CASCADE)
    text=models.TextField()
    req=models.ForeignKey(Req,related_name='comment_have_req',on_delete=models.CASCADE)
    
    

