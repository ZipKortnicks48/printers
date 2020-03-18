from django.contrib import admin
from .models import WorkUnit,ModelPrinter,Producer
# Register your models here.
admin.site.register(WorkUnit)
admin.site.register(ModelPrinter)
admin.site.register(Producer)