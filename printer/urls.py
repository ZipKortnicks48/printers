from django.urls import path
from .views import WorkUnitView,ModelCartridgeView,BrokeView,DiagnosticView,ServView,WaitingView, DeleteView, ServUsView,RetView,MoveView,OrderCartridgeView,CartridgesListView
from .views import CartridgeClose,CartridgeRefill,CartridgeComeback,CartridgeCancel,CartridgeComebackAll,CartridgeActsView,CartridgeRefillAll,CartridgeTableEdit,ActEditStatus
from .views import CartridgeActsViewAdmin2,CartridgeActsViewAdmin
app_name = "printer"
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('', WorkUnitView.as_view()),
    #path('cartridges/',ModelCartridgeView.as_view()),
    path('cartridges/',CartridgesListView.as_view()),
    path('broke/',BrokeView.as_view()),
    path('order/',OrderCartridgeView.as_view()),
    path('order_list/',CartridgeActsView.as_view()),
    # админское 
    path('diagn/',DiagnosticView.as_view()),
    path('serv/',ServView.as_view()),
    path('wait/',WaitingView.as_view()),
    path('servus/',ServUsView.as_view()),
    path('ret/',RetView.as_view()),
    path('move/',MoveView.as_view()),
    path('del/',DeleteView.as_view()),

    path('cartridgerefillview/',CartridgeActsViewAdmin.as_view()),
    path('cartridgederefillview/',CartridgeActsViewAdmin2.as_view()),
    path('close/',CartridgeClose.as_view()),
    # path('refill/',CartridgeRefill.as_view()),
    # path('comeback/',CartridgeComeback.as_view()),
    path('tableedit/',CartridgeTableEdit.as_view()),
    path('cancel/',CartridgeCancel.as_view()),
    path('comebackall/',CartridgeComebackAll.as_view()),
    path('refilall/',CartridgeRefillAll.as_view()),
    path('editstatus/',ActEditStatus.as_view()),
    
]
