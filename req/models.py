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
    deadline=models.DateField()
    finishdate=models.DateField(blank=True,default=datetime.date.today)
    cabinet=models.ForeignKey(Cabinet,related_name="req_have_cabinet",on_delete=models.CASCADE)
    user=models.ForeignKey(User,related_name="req_have_user",on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    checkout=models.BooleanField(default=False)
    def __str__(self):
        cabinet=Cabinet.objects.get(id=self.cabinet.id)
        return str(self.id)+". "+cabinet.__str__()+" - "+self.shortname

class Comment(models.Model):
    date=models.DateField(default=datetime.date.today)
    user=models.ForeignKey(User,related_name="comment_have_user",on_delete=models.CASCADE)
    text=models.TextField()
    req=models.ForeignKey(Req,related_name='comment_have_req',on_delete=models.CASCADE)
    
    

