from django.contrib import admin
from .models import WorkUnit,ModelPrinter,Producer,ModelCartridge,ActPrinter,ActCartridge
# Register your models here.
admin.site.register(WorkUnit)
admin.site.register(ModelPrinter)
admin.site.register(Producer)
admin.site.register(ModelCartridge)
admin.site.register(ActPrinter)
admin.site.register(ActCartridge)