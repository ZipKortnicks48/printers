from django.db import models
from users.models import User
from city.models import Cabinet
from django.utils import timezone
# Create your models here.

class Req(models.Model):
    shortname = models.CharField(max_length=255)
    description=models.TextField()
    date=models.DateField(default=timezone.now)
    deadline=models.DateField()
    cabinet=models.ForeignKey(Cabinet,related_name="req_have_cabinet",on_delete=models.CASCADE)
    user=models.ForeignKey(User,related_name="req_have_user",on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    checkout=models.BooleanField(default=False)
    def __str__(self):
        return self.shortname

