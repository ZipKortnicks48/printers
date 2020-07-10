from django.urls import path
from .views import WorkUnitView,ModelCartridgeView,BrokeView,DiagnosticView,ServView,WaitingView, DeleteView, ServUsView,RetView,MoveView
app_name = "printer"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('', WorkUnitView.as_view()),
    path('cartridges/',ModelCartridgeView.as_view()),
    path('broke/',BrokeView.as_view()),
    # админское 
    path('diagn/',DiagnosticView.as_view()),
    path('serv/',ServView.as_view()),
    path('wait/',WaitingView.as_view()),
    path('servus/',ServUsView.as_view()),
    path('ret/',RetView.as_view()),
    path('move/',MoveView.as_view()),
    path('del/',DeleteView.as_view()),
]
