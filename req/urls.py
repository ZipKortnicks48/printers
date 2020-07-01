from django.urls import path
from .views import ReqView, SingleReqView, CommentView, ReqAdminView,ReqAppointView,ReqCloseView
app_name = "req"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('', ReqView.as_view()),
    path('<int:pk>',SingleReqView.as_view()),
    path('comments/',CommentView.as_view()),
    # админское 
    path('admin_view/',ReqAdminView.as_view()),
    path('admin_appoint/',ReqAppointView.as_view()),
    path('admin_req_close/',ReqCloseView.as_view())
]
