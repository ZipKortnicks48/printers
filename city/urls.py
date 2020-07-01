from django.urls import path
from .views import CabinetView, CitiesView,CabinetInSelectedCityView
app_name = "city"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('cabinets/', CabinetView.as_view()),
    path('list/',CitiesView.as_view()),
    path('cabinets_by_cities/',CabinetInSelectedCityView.as_view())
]
