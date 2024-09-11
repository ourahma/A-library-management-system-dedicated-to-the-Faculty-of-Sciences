from django.urls import path
from . import views
urlpatterns = [
   path('',views.cart_summary,name='cart_summary'),
   path('add/',views.cart_add,name='cart_add'),
   path('delete/',views.cart_delete,name='cart_delete'),
   path('deleteAll/',views.deleteAllfromBin,name='deleteAllfromBin'),
   path('reserverAll/',views.reserver_tous,name='reserverAll'),
   path('reserver_exemplaire/', views.reserver_exemplaire, name='reserver_exemplaire'),
   path('emprunter_un/',views.emprunter,name='emprunter_un'),
   path('emprunter_tous/',views.emprunter_tous,name='emprunter_tous'),
   path('consulter_staff/',views.consulter,name='consulter_staff'),
   path('modifier_reservation/', views.modifier_reservation, name='modifier_reservation'),
]  