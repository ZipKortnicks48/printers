from django.urls import path
from .views import CabinetView
app_name = "city"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('cabinets/', CabinetView.as_view())
]
