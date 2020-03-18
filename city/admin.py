from django.contrib import admin

# Register your models here.
from .models import City,Cabinet
admin.site.register(City)
admin.site.register(Cabinet)