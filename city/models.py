from django.db import models
# Create your models here.

class City(models.Model):
    name = models.CharField(max_length=255)
    email_city=models.CharField(max_length=50,default='')
    def __str__(self):
        return self.name
class Cabinet(models.Model):
    name = models.CharField(max_length=255)
    number=models.IntegerField()
    city=models.ForeignKey(City,related_name="cabinet_have_city",on_delete=models.CASCADE)
    def __str__(self):
        city=City.objects.get(id=self.city.id)
        return self.city.name+":"+self.name 