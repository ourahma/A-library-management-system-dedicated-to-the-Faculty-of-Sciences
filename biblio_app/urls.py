from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from . import views

urlpatterns = [
    path('',views.index, name='home'),
    path('apropos/', views.apropos, name='apropos'),
    path('contacteznous/', views.contacteznous, name='contacteznous'),
    path('ouvrage/<str:foo>',views.afficher_ouvrage,name='ouvrage'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/',views.logout_user,name='logout_user'),
    path('login_user/',views.LoginView.as_view(),name='login_user'),



    
    ####### Password reset by email
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    
    
    ### activate user email through email
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    path('update_profile/',views.UpdateUser.as_view(),name='update_profile'),
    path('update_paswd/',views.UpdatePswd.as_view(),name='update_paswd'),
    path('search/', views.search, name='search'),
    path('gerer/', views.GererReservations.as_view(), name='gerer'),
    path('emprunts/', views.GererEmptunts.as_view(), name='emprunts'),
    path('reservation/annuler', views.AnnulerReservations.as_view(), name='annuler_reservation'),
    path('signaler_perte/', views.SignalerPerte.as_view(), name='signaler_perte'),
    path('signlaer_deterioration/', views.SignalerDeterioration.as_view(), name='signlaer_deterioration'),
    #liens pour categorie
    path('categorie/',views.categorie,name='categorie'),
    path('ajouter_categorie/', views.ajouter_categorie, name='ajouter_categorie'),
    path('modifier_categorie/', views.modifier_categorie,name='modifier_categorie'),
    path('supprimer_categorie/<id_categorie>/', views.supprimer_categorie,name='supprimer_categorie'),
    #liens our gestion de Bibliothecaire
    path('bibliothecaire/', views.bibliothecaire, name='bibliothecaire'),
    path('ajouter_bibliothecaire/', views.ajouter_bibliothecaire, name='ajouter_bibliothecaire'),
    path('modifier_bibliothecaire/', views.modifier_bibliothecaire, name='modifier_bibliothecaire'),
    path('supprimer_bibliothecaire/<str:id_bibliothecaire>/', views.supprimer_bibliothecaire, name='supprimer_bibliothecaire'),



    ##Signlement
    path('Signalement/', views.signalement, name='Signalement'),
    path("modifier_signalement",views.modifier_signalement,name='modifier_signalement'),
    path('supprimer_signalement/', views.supprimer_signalement, name='supprimer_signalement'),



    #liens pour emprunter
    path('reservations/',views.emprunt,name='reservations'),
    path('reservation_to_emprunt/<int:id_reservation>/', views.reservation_to_emprunt, name='reservation_to_emprunt'),
    path('rejeter_reservation/<int:id_reservation>/', views.rejeter_reservation, name='rejeter_reservation'),
    path('liste_emprunt/', views.liste_emprunt, name='liste_emprunt'),
    path('emprunts_overdue/', views.emprunts_overdue, name='emprunts_overdue'),
    path('modifier_emprunt/', views.modifier_emprunt, name='modifier_emprunt'),
    path('supprimer_emprunt/<id_emprunt>/', views.supprimer_emprunt, name='supprimer_emprunt'),
    path('rendre_emprunt/<id_emprunt>/', views.rendre_emprunt, name='supprimer_emprunt'),
    path('overdue_emprunt/', views.overdue_emprunt, name='overdue_emprunt'),
    path('prolonger_date_retour/', views.prolonger_date_retour, name='prolonger_date_retour'),
    #dash
    path('administration/', views.dash, name='admin'),
     #ouvrage 
    path('ouvrage/', views.ouvrage, name='ouvrage'),
    path('add_ouvrage/', views.add_ouvrage, name='add_ouvrage'),
    path('modifier_ouvrage/', views.modifier_ouvrage, name='modifier_ouvrage'),
    path('supprimer_ouvrage/<str:ISBN>/', views.supprimer_ouvrage, name='supprimer_ouvrage'),
    #exemplaires
    path('exemplaire/', views.exemplaire, name='exemplaire'),
    path('add_exemplaire/', views.add_exemplaire, name='add_exemplaire'),
    path('modify_exemplaire/', views.modifier_exemplaire, name='modifier_exemplaire'),
    path('delete_exemplaire/<str:id_exemplaire>/', views.delete_exemplaire, name='delete_exemplaire'),
    #historique
    path('historique/', views.historique, name='historique'),


    #consultation
    path('liste_consultation/', views.liste_consultation, name='liste_consultation'),
    path('consulter/', views.consulter, name='consulter'),
    path('supprimer_consultation/<int:id_consultation>/', supprimer_consultation, name='supprimer_consultation'),
    path('rendre_consultation/<id_consultation>/', views.rendre_consultation, name='rendre_consultation'),
    path('modifier_consultation/', views.modifier_consultation, name='modifier_consultation'),
    
    #notifications
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('send_notification/', views.send_notification, name='send_notification'),
     
     #adminsup
    path('adminsup/', views.AdminSupsView, name='adminsup'),
    path('add_adminsup/', views.ajouter_adminsup, name='add_adminsup'),
    path('modify_adminsup/', views.modify_adminsup, name='modify_adminsup'),
    path('delete_adminsup/<str:id>/', views.DeleteAdminSupView.as_view(), name='delete_adminsup'),


     #utilisateurs
    path('utilisateurs/', views.utilisateurs, name='utilisateurs'),
    path('modifier_utilisateur/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('bannir_utilisateur/<str:id>/', views.bannir_utilisateur, name='bannir_utilisateur'),
    path('debannir_utilisateur/<str:id>/', views.debannir_utilisateur, name='debannir_utilisateur'),
    path('supprimer_utilisateur/<str:id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
]
