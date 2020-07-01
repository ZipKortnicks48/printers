from django.urls import path
from .views import CreateUserAPIView,authenticate_user, FindAdminUserAPIView
app_name = "users"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('auth/', authenticate_user),
    path('register/',CreateUserAPIView.as_view()),
    path('get_admins/',FindAdminUserAPIView.as_view())
]
