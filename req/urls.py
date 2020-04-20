from django.urls import path
from .views import ReqView, SingleReqView, CommentView
app_name = "req"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('', ReqView.as_view()),
    path('<int:pk>',SingleReqView.as_view()),
    path('comments/',CommentView.as_view())
]
