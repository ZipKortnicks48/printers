from django.db import models
from django.utils import timezone
from city.models import Cabinet
import datetime
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
    printer=models.ForeignKey(ModelPrinter,related_name="workunit_have_modelprinter",on_delete=models.CASCADE)
    cabinet=models.ForeignKey(Cabinet,related_name="workunit_have_cabinet",on_delete=models.CASCADE)
    status=models.IntegerField(default=1)
    color=models.CharField(max_length=20,default="",null=True)
    note=models.CharField(max_length=255,default="",null=True)# служебный комменатрий
    status_note=models.CharField(max_length=255,default="",null=True,) #комментарий к состоянию принтера
    # 1 - в работе, 2 - сломан, 3 - диагностика, 4 - ремонт, 5 - ожидает, 6 - списан
    def __str__(self):
        return self.cabinet.city.name+" "+str(self.cabinet.name)+" "+self.printer.name+" " + str(self.printer.id) 
class ModelCartridge(models.Model):
    name=models.CharField(max_length=20,unique=True)
    count=models.IntegerField(default=0)
    printer=models.ForeignKey(ModelPrinter,related_name="modelcartridge_have_modelprinter",on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class ActPrinter(models.Model):
    date=models.DateField(default=datetime.date.today)
    status=models.IntegerField(default=1)
    # 1 - акт перемещения принтера из кабинета в другой кабинет или в комплекс,
    # 2 - акт поломки, обнаруженной в комплексе,
    # 3 - акт принятия на диагностику, 4 - акт сдачи в ремонт, 5 - акт принятия из ремонта,
    # 6 - акт самостоятельного устранения ошибки с указанием поломки
    # 7 - акт списания при полной неработоспособности принтера 
    comment=models.CharField(max_length=255,default="",null=True)#комментарий об изменении состояния принтера и/или его местонахождении
    printer=models.ForeignKey(WorkUnit,related_name="actprinter_have_workunit",on_delete=models.CASCADE)
    def __str__(self):
        if self.status==1:
            return str(self.date)+" Перемещение"
        if self.status==2:
            return str(self.date)+" Поломка в комплексе"
        if self.status==3:
            return str(self.date)+" Принятие на диагностику"
        if self.status==4:
            return str(self.date)+" Сдача в ремонт"
        if self.status==5:
            return str(self.date)+" Принятие из ремонта"
        if self.status==6:
            return str(self.date)+" Самостоятельное исправление ошибки"
        if self.status==7:
            return str(self.date)+" Списание"
        