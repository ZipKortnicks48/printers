from django.db import models
from city.models import Cabinet
# Create your models here.

class Producer(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
class ModelPrinter(models.Model):
    name = models.CharField(max_length=255)
    producer=models.ForeignKey(Producer,related_name="modelprinter_have_producer",on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class WorkUnit(models.Model):
    name = models.CharField(max_length=255)
    model=models.ForeignKey(ModelPrinter,related_name="workunit_have_modelprinter",on_delete=models.CASCADE)
    cabinet=models.ForeignKey(Cabinet,related_name="workunit_have_cabinet",on_delete=models.CASCADE)
    state=models.IntegerField(default=0)
    def __str__(self):
        return self.name
