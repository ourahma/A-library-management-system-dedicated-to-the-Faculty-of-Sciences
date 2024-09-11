import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from django.contrib.auth import views as auth_views
from django.db import DatabaseError
from .models import Notification
from django.views.decorators.http import require_POST
from django.utils.functional import SimpleLazyObject
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from django.core.exceptions import *
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import *
from cart.cart import *

from .tokens import account_activation_token

from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_variables
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.forms import *
from django.shortcuts import render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.cache import cache_control, never_cache
from django.utils.decorators import method_decorator
from django.core.cache import cache
import re

from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.utils.encoding import force_bytes, force_str

from django.conf import settings

#-----------------------------------------------COTE ADMINISTRATION----------------------------------------
@login_required
def is_Staff(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'BIBLIOTHECAIRE' or request.user.role == 'ADMINSUP':
        return True
    else:
        return False
    

def is_staff_no_auth(request):
    if request.user.is_authenticated and (request.user.role == 'BIBLIOTHECAIRE' or request.user.role == 'ADMINSUP'):
        return True
    else:
        return False


@login_required
def is_adminSup(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'ADMINSUP':
        return True
    else:
        return False
    
@login_required
def is_bibliothecaire(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'BIBLIOTHECAIRE':
        return True
    else:
        return False


@login_required    
def overdue_emprunt(request):
    if is_Staff(request):
        try:
            overdue_emprunts = Emprunter.objects.filter(date_retour__lt=timezone.now()).values()
            overdue_emprunts_length = len(overdue_emprunts)
            return JsonResponse({'overdue_emprunts_length': overdue_emprunts_length})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des emprunts en retard.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


# DASHBOARD
@login_required
def dash(request):
    if is_Staff(request): 
        try:
            ouvrages = Ouvrage.objects.all()
            print(ouvrages)
            categories = Categorie.objects.all()
            return render(request, 'admin_dash.html', {'ouvrages': ouvrages, 'categories': categories})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des données.")
            return redirect('home')
    else:
        return redirect('home')


@login_required
def bibliothecaire(request):
    if is_adminSup(request):
        try:
            bibliothecaires = Personne.objects.filter(role='BIBLIOTHECAIRE')
            paginator = Paginator(bibliothecaires, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            bibliothecaires_list = paginator.get_page(page_number)
            return render(request, 'bibliothecaire.html', {'bibliothecaires': bibliothecaires_list})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des bibliothécaires.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def ajouter_bibliothecaire(request):
    if is_adminSup(request):
        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:
                Personne.objects.get(email=email)
                messages.error(request, "L'email est déjà utilisé.")
                return JsonResponse({'error': "L'email est déjà utilisé."}, status=400)
            except ObjectDoesNotExist:
                Personne.Ajouter_bibliothecaire(nom, prenom, telephone, email, password)
                messages.success(request, 'Bibliothecaire ajouté avec succès.')
                return JsonResponse({'message': 'Bibliothecaire ajouté avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de l'ajout du bibliothécaire.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, "Méthode erronée.")
            return JsonResponse({'error': 'Méthode erronée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def signalement(request):
    if is_Staff(request):
        try:
            signalement_list = Signalement.objects.all().order_by("id")
            ouvrages=Ouvrage.objects.all()
            exemplaires=Exemplaire.objects.all()
            paginator = Paginator(signalement_list, 10)  

            page_number = request.GET.get('page')
            signalements = paginator.get_page(page_number)

            return render(request, 'signalement.html', {'signalements': signalements,'ouvrages':ouvrages,'exemplaires':exemplaires})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des signalement.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def modifier_signalement(request):
    if request.method == "POST":
        personne=Personne.objects.get(id=request.user.id)
        id_signalement = request.POST.get('id_signalement')
        
        signalement = Signalement.objects.get(id=id_signalement)
        perdu = 'perdu' in request.POST
        deteriorie = 'deteriorie' in request.POST
        print(perdu)
        print(deteriorie)
        exemplaire = signalement.exemplaire
        if not perdu and not deteriorie:
            code,message=personne.supprimer_signalement(id_signalement)
            response_data = {
            'success': True,
            'message': message,
        }
            messages.success(request,message)
            return JsonResponse(response_data)
        else:
            exemplaire.perdu = perdu
            exemplaire.deteriore = deteriorie
            exemplaire.save()
            message="Modification faites aves succés"
            messages.success(request,message )
            response_data = {
            'success': True,
            'message': message,
        }
            return JsonResponse(response_data)
        
import json
def supprimer_signalement(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        id_signalement = data.get('id_signalement')
        
        personne=Personne.objects.get(id=request.user.id)
        code ,message=personne.supprimer_signalement(id_signalement)

        if code==1:
            messages.success(request,message)
            return JsonResponse({'success': True, 'message': message})
        else:
            messages.error(request,message)
            return JsonResponse({'success': False, 'message': message})
    
def modifier_bibliothecaire(request):
    if is_adminSup(request):
        ad_id = request.POST.get('id_bibliothecaire')
        try:
            bibliothecaire = Personne.objects.get(id=ad_id, role='BIBLIOTHECAIRE')
        except ObjectDoesNotExist:
            messages.error(request, "Bibliothécaire introuvable.")
            return JsonResponse({'error': "Bibliothécaire introuvable."}, status=400)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération du bibliothécaire.")
            return JsonResponse({'error': str(e)}, status=500)

        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:
                user = Personne.objects.get(email=bibliothecaire.email)
                exists = Personne.objects.filter(email=email).exclude(id=user.id).exists()
                if exists:
                    messages.error(request, "L'email est déjà utilisé.")
                    return JsonResponse({'error': "L'email est déjà utilisé."}, status=400)
                adminsup = Personne()
                if password:
                    adminsup.Modifier_bibliothecaire(ad_id, n_nom=nom, n_prenom=prenom, n_telephone=telephone, n_email=email, n_password=password)
                else:
                    adminsup.Modifier_bibliothecaire(ad_id, n_nom=nom, n_prenom=prenom, n_telephone=telephone, n_email=email)
                messages.success(request, 'Bibliothecaire modifié avec succès.')
                return JsonResponse({'message': 'Bibliothecaire modifié avec succès.'}, status=200)
            except ObjectDoesNotExist:
                messages.error(request, "Personne introuvable.")
                return JsonResponse({'error': "Personne introuvable."}, status=400)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification du bibliothécaire.")
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def supprimer_bibliothecaire(request, id_bibliothecaire):
    if is_adminSup(request):
        if request.method == 'DELETE':
            try:
                adminsup = Personne()
                adminsup.supprimer_bibliothecaire(id=id_bibliothecaire)
                messages.success(request, 'Bibliothecaire supprimé avec succès.')
                return JsonResponse({'message': 'Bibliothecaire supprimé avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression du bibliothécaire.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


# les méthodes de réservations
@login_required
def reservations(request):
    if is_bibliothecaire(request):
        try:
            reservations_query = Reservation.objects.all().order_by('id_reservation')
            return render(request, 'reservations.html', {'reservations': reservations_query})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des réservations.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


# les méthodes de emprunt
@login_required
def emprunt(request):
    if is_bibliothecaire(request):
        try:
            reservations_list = Reservation.objects.all().order_by('id_reservation')
            paginator = Paginator(reservations_list, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            reservations = paginator.get_page(page_number)
            return render(request, 'liste_reservations.html', {'reservations': reservations})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des réservations.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def reservation_to_emprunt(request, id_reservation):
    if is_bibliothecaire(request):
        try:
            reservation = Reservation.objects.get(id_reservation=id_reservation)
            done, consulter, message = Emprunter.emprunter(id_bibliothecaire=request.user.email, id_ouvrage=reservation.ouvrage.ISBN, id_utilisateur=reservation.id_utilisateur.email)
            if done:
                reservation.delete()
                messages.success(request, message)
                return JsonResponse({'message': message}, status=200)
            elif consulter == 1:
                messages.error(request, message)
                return JsonResponse({'consulter': message}, status=400)
            else:
                messages.error(request, message)
                return JsonResponse({'error': message}, status=500)
        except ObjectDoesNotExist:
            messages.error(request, "Réservation introuvable.")
            return JsonResponse({'error': "Réservation introuvable."}, status=400)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération de la réservation.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def rejeter_reservation(request, id_reservation):
    if is_bibliothecaire(request):
        if request.method == 'DELETE':
            try:
                Reservation.delete_reservation(Reservation, reservation_id=id_reservation)
                messages.success(request, 'Réservation rejetée avec succès.')
                return JsonResponse({'message': 'Réservation rejetée avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors du rejet de la réservation.")
                return JsonResponse({'error': str(e)}, status=500)
        
        messages.error(request, 'Méthode non autorisée.')
        return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


#liste des emprunts
@login_required
def liste_emprunt(request):
    if is_bibliothecaire(request):
        try:
            emprunt_list = Emprunter.objects.all().order_by('id_emprunt')
            ouvrages = Ouvrage.objects.all()
            exemplaires = Exemplaire.objects.all()
            paginator = Paginator(emprunt_list, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            emprunts = paginator.get_page(page_number)
            return render(request, 'liste_emprunt.html', {'emprunts': emprunts, 'ouvrages': ouvrages, 'exemplaires': exemplaires, 'showing': True})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des emprunts.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


@login_required
def emprunts_overdue(request):
    if is_Staff(request):
        try:
            emprunt_list = Emprunter.objects.filter(date_retour__lt=timezone.now(), rendu=False)
            ouvrages = Ouvrage.objects.all()
            exemplaires = Exemplaire.objects.all()
            paginator = Paginator(emprunt_list, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            emprunts = paginator.get_page(page_number)
            return render(request, 'liste_emprunt.html', {'emprunts': emprunts, 'ouvrages': ouvrages, 'exemplaires': exemplaires, 'showing': False})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des emprunts en retard.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def modifier_emprunt(request):
    if is_bibliothecaire(request):
        emp_id = request.POST.get('id_emprunt')
        try:
            emprunt = Emprunter.objects.get(id_emprunt=emp_id)
        except ObjectDoesNotExist:
            messages.error(request, "Emprunt introuvable.")
            return JsonResponse({'error': "Emprunt introuvable."}, status=400)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération de l'emprunt.")
            return JsonResponse({'error': str(e)}, status=500)

        if request.method == 'POST':
            id_exp = request.POST.get('id_exp')
            id_ouvrage = request.POST.get('id_o')
            id_bibliothecaire = request.user.email
            new_date = request.POST.get('date_s')
            print(new_date)
            rendu = request.POST.get('rendu')
            rendu = True if rendu else False
            
            try:
                if rendu :
                    done=emprunt.modifier_emprunt(id_exemplaire=id_exp, id_ouvrage=id_ouvrage, id_bibliothecaire=id_bibliothecaire, new_date=new_date, rendu=rendu)
                else :
                    done=emprunt.modifier_emprunt(id_exemplaire=id_exp, id_ouvrage=id_ouvrage, id_bibliothecaire=id_bibliothecaire, new_date=new_date)
                if done:

                    messages.success(request, 'Emprunt modifié avec succès.')
                    return JsonResponse({'message': 'Emprunt modifié avec succès.'}, status=200)
                else:
                    messages.error(request, 'Emprunt n\'est empruntable donc vous ne pouvez pas le modifier.')
                    return JsonResponse({'message': 'Emprunt modifié avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification de l'emprunt.")
                return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def rendre_emprunt(request, id_emprunt):
    if is_bibliothecaire(request):
        try:
            Emprunter.Retourner_Emprunt(id_emprunt=id_emprunt)
            messages.success(request, 'Emprunt enregistrée!')
            return JsonResponse({'message': 'Emprunt enregistrée!'}, status=200)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de l'enregistrement de l'emprunt.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def supprimer_emprunt(request, id_emprunt):
    if is_bibliothecaire(request):
        if request.method == 'DELETE':
            try:
                Emprunter.Annuler_Emprunt(id_emprunt=id_emprunt)
                messages.success(request, 'Emprunt supprimé avec succès.')
                return JsonResponse({'message': 'Emprunt supprimé avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression de l'emprunt.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


# Les méthodes de categorie
@login_required
def categorie(request):
    if is_Staff(request):
        try:
            categories_list = Categorie.objects.all().order_by('id_categorie')
            paginator = Paginator(categories_list, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            categories = paginator.get_page(page_number)

            return render(request, 'categorie.html', {'categories': categories})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des catégories.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def ajouter_categorie(request):
    if is_Staff(request):
        if request.method == 'POST':
            try:
                nom = request.POST.get('nom_categorie')
                description = request.POST.get('description_categorie')
                Categorie.Ajouter_Categorie(nom_categorie=nom, description_categorie=description)
                messages.success(request, 'Catégorie ajoutée avec succès.')
                return JsonResponse({'message': 'Catégorie ajoutée avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de l'ajout de la catégorie.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=400)


def modifier_categorie(request):
    if is_Staff(request):
        try:
            categorie_id = request.POST.get('id_categorie')
            categorie = Categorie.objects.get(id_categorie=categorie_id)
        except ObjectDoesNotExist:
            messages.error(request, "Catégorie introuvable.")
            return JsonResponse({'error': "Catégorie introuvable."}, status=400)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération de la catégorie.")
            return JsonResponse({'error': str(e)}, status=500)

        if request.method == 'POST':
            try:
                nom = request.POST.get('nom_categorie')
                description = request.POST.get('description_categorie')
                categorie.modifier_categorie(categorie_id, nouveau_nom=nom, nouvelle_description=description)
                messages.success(request, 'Catégorie modifiée avec succès.')
                return JsonResponse({'message': 'Catégorie modifiée avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification de la catégorie.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def supprimer_categorie(request, id_categorie):
    if is_Staff(request):
        if request.method == 'DELETE':
            try:
                Categorie.supprimer_categorie(Categorie, categorie_id=id_categorie)
                messages.success(request, 'Catégorie supprimée avec succès.')
                return JsonResponse({'message': 'Catégorie supprimée avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression de la catégorie.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


@login_required
def ouvrage(request):
    if is_Staff(request):
        try:
            ouvrages = Ouvrage.objects.all()
            categories = Categorie.objects.all()
            paginator = Paginator(ouvrages, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            ouvrages_list = paginator.get_page(page_number)
            return render(request, 'ouvrage.html', {'ouvrages': ouvrages_list, 'categories': categories})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des ouvrages.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def add_ouvrage(request):
    print("add ouvrage methode")
    if is_Staff(request):
        if request.method == 'POST':
            try:
                # Extract form data from request.POST
                ISBN = request.POST.get('ISBN')
                titre = request.POST.get('titre')
                auteur = request.POST.get('auteur')
                edition = request.POST.get('edition')
                num_exemplaire=request.POST.get('num_exemplaire')
                type = request.POST.get('type')
                categorie_id = request.POST.get('categorie')
                categorie = Categorie.objects.get(id_categorie=categorie_id)
                image = request.FILES.get('image')
                description = request.POST.get('description')
                exists = Ouvrage.objects.filter(ISBN=ISBN).exists()
                if exists :
                    messages.error(request,'Un ouvrage avec le même ISBN existe déja')
                    return JsonResponse({'error': 'Un ouvrage avec le même ISBN existe déja'}, status=400)
                exists = Ouvrage.objects.filter(titre=titre,auteur=auteur,edition=edition,categorie=categorie).exclude(ISBN=ISBN).exists()
                if exists :
                    messages.error(request,'Cet ouvrage existe déja')
                    return JsonResponse({'error': 'Cet ouvrage existe déja'}, status=400)
                
                Ouvrage.ajouter_ouvrage(Ouvrage, titre, auteur, edition, ISBN, type, categorie, image, description)
                messages.success(request, 'Ouvrage ajouté avec succès!')
                return JsonResponse({'message': 'Ouvrage ajouté avec succès!'}, status=200)
            except ObjectDoesNotExist:
                messages.error(request, "Catégorie introuvable.")
                return JsonResponse({'error': "Catégorie introuvable."}, status=400)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de l'ajout de l'ouvrage.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def modifier_ouvrage(request):
    if is_Staff(request):
        if request.method == 'POST':
            try:
                # Extract form data from request.POST
                isbn_g = request.POST.get('ISBN')
                titre = request.POST.get('titre')
                auteur = request.POST.get('auteur')
                edition = request.POST.get('edition')
                type = request.POST.get('type')
                nouvelle_categorie_id = request.POST.get('categorie')
                categorie = Categorie.objects.get(id_categorie=nouvelle_categorie_id)
                image = request.FILES.get('image')
                description = request.POST.get('description')

                exists = Ouvrage.objects.filter(titre=titre,auteur=auteur,edition=edition,categorie=categorie).exclude(ISBN=isbn_g).exists()
                if exists :
                    messages.error(request,'Cet ouvrage existe déja')
                    return JsonResponse({'error': 'Cet ouvrage existe déja'}, status=400)

                Ouvrage.modifier_ouvrage(Ouvrage, isbn_g, titre, auteur, edition, type, categorie, image, description)
                messages.success(request, 'Ouvrage modifié avec succès!')
                return JsonResponse({'message': 'Ouvrage modifié avec succès!'}, status=200)
            except ObjectDoesNotExist:
                messages.error(request, "Catégorie introuvable.")
                return JsonResponse({'error': "Catégorie introuvable."}, status=400)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification de l'ouvrage.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def supprimer_ouvrage(request, ISBN):
    if is_Staff(request):
        if request.method == 'DELETE':
            try:
                done = Ouvrage.supprimer_ouvrage(Ouvrage, ISBN=ISBN)
                if done:
                    messages.success(request, 'Ouvrage supprimé avec succès!')
                    return JsonResponse({'message': 'Ouvrage supprimé avec succès!'}, status=200)
                else:
                    messages.error(request, "Echec de suppression de l'ouvrage.")
                    return JsonResponse({'error': "Echec de suppression de l'ouvrage."}, status=500)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression de l'ouvrage.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


# Exemplaire
@login_required
def exemplaire(request):
    if is_Staff(request):
        try:
            exemplaires = Exemplaire.objects.all()
            ouvrages = Ouvrage.objects.all()
            paginator = Paginator(exemplaires, 10)  # Show 10 categories per page

            page_number = request.GET.get('page')
            exemplaires_list = paginator.get_page(page_number)
            return render(request, 'exemplaire.html', {'exemplaires': exemplaires_list, 'ouvrages': ouvrages})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des exemplaires.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def add_exemplaire(request):
    if is_Staff(request):
        if request.method == 'POST':
            try:
                # Extract form data from request.POST
                deteriore_checked = request.POST.get('deteriore')
                deteriore = True if deteriore_checked else False

                emprunte_checked = request.POST.get('empruntable')
                empruntable = True if emprunte_checked else False

                perdu_checked = request.POST.get('perdu')
                perdu = True if perdu_checked else False

                ouvrage_id = request.POST.get('ouvrage')
                ouvrage = Ouvrage.objects.get(ISBN=ouvrage_id)

                disponible_checked = request.POST.get('disponible')
                disponible = True if disponible_checked else False

                nombre = int(request.POST.get('nombre'))
                print("nombre",nombre)
                for i in range(1, nombre + 1):
                    
                    Exemplaire.add_exemplaire(deteriore=deteriore, perdu=perdu, empruntable=empruntable, ouvrage=ouvrage, disponible=disponible)

                messages.success(request, 'Exemplaire ajouté avec succès!')
                return JsonResponse({'message': 'Exemplaire ajouté avec succès!'}, status=200)
            except ObjectDoesNotExist:
                messages.error(request, "Ouvrage introuvable.")
                return JsonResponse({'error': "Ouvrage introuvable."}, status=400)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de l'ajout de l'exemplaire.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def modifier_exemplaire(request):
    if is_Staff(request):
        try:
            id_ex = request.POST.get('id_exemplaire')
            print(id_ex)
            exemplaire = Exemplaire.objects.get(id_exemplaire=id_ex)
        except ObjectDoesNotExist:
            messages.error(request, "Exemplaire introuvable.")
            return JsonResponse({'error': "Exemplaire introuvable."}, status=400)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération de l'exemplaire.")
            return JsonResponse({'error': str(e)}, status=500)

        if request.method == 'POST':
            try:
                # Extract form data from request.POST
                deteriore_checked = request.POST.get('deteriore')
                deteriore = True if deteriore_checked else False

                emprunte_checked = request.POST.get('empruntable')
                empruntable = True if emprunte_checked else False

                perdu_checked = request.POST.get('perdu')
                perdu = True if perdu_checked else False

                nouvelle_ouvrage_id = request.POST.get('ouvrage')
                ouvrage = Ouvrage.objects.get(ISBN=nouvelle_ouvrage_id)

                disponible_checked = request.POST.get('disponible')
                disponible = True if disponible_checked else False
               
                exemplaire.Modifier_exemplaire(id_ex=id_ex, ndeteriore=deteriore, nperdu=perdu, nempruntable=empruntable, nouvrage=ouvrage, ndisponible=disponible)
                messages.success(request, 'Exemplaire modifié avec succès!')
                return JsonResponse({'message': 'Exemplaire modifié avec succès!'}, status=200)
            except ObjectDoesNotExist:
                messages.error(request, "Ouvrage introuvable.")
                return JsonResponse({'error': "Ouvrage introuvable."}, status=400)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification de l'exemplaire.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)
     

def delete_exemplaire(request, id_exemplaire):
    if is_Staff(request):
        if request.method == 'DELETE':
            try:
                bibliothecaire = Personne()
                exemplaire = Exemplaire.objects.get(id_exemplaire=id_exemplaire)
                done = exemplaire.delete_exemplaire(id_exemplaire=id_exemplaire)
                if done:
                    messages.success(request, 'Exemplaire supprimé avec succès!')
                    return JsonResponse({'message': 'Exemplaire supprimé avec succès.'}, status=200)
                else:
                    messages.error(request, 'Échec lors de la suppression de l\'exemplaire.')
                    return JsonResponse({'error': 'Échec lors de la suppression de l\'exemplaire.'}, status=500)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression de l'exemplaire.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def liste_consultation(request):
    if is_bibliothecaire(request):
        try:
            consultation_list = Consulter.objects.all().order_by('id_consultation')
            ouvrages = Ouvrage.objects.all()
            exemplaires = Exemplaire.objects.all()
            paginator = Paginator(consultation_list, 10)  # Show 10 consultations per page

            page_number = request.GET.get('page')
            consultations = paginator.get_page(page_number)
            return render(request, 'liste_consultation.html', {'consultations': consultations, 'ouvrages': ouvrages, 'exemplaires': exemplaires, 'showing': True})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des consultations.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def rendre_consultation(request, id_consultation):
    if is_bibliothecaire(request):
        if request.method == 'GET':
            try:
                consultation = Consulter.objects.get(id_consultation=id_consultation)
                success = Consulter.retourner_consultation(consultation.id_consultation)
                if success:
                    messages.success(request, 'Consultation retournée avec succès.')
                    return JsonResponse({'message': 'Consultation retournée avec succès.'}, status=200)
                else:
                    messages.error(request, 'Impossible de retourner la consultation.')
                    return JsonResponse({'error': 'Impossible de retourner la consultation.'}, status=500)
            except Consulter.DoesNotExist:
                messages.error(request, 'Consultation non trouvée.')
                return JsonResponse({'error': 'Consultation non trouvée.'}, status=404)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors du retour de la consultation.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode incorrecte.')
            return JsonResponse({'error': 'Méthode incorrecte.'}, status=405)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


def modifier_consultation(request):
    if is_bibliothecaire(request):
        if request.method == 'POST':
            logger.info('Requête POST reçue')
            try:
                id_consultation = request.POST.get('consultationId')
                consultation = Consulter.objects.get(id_consultation=id_consultation)
                id_exemplaire = request.POST.get('exemplaire')
                id_ouvrage = request.POST.get('ouvrage')
                id_bibliothecaire = request.user.email
                dateSortie = request.POST.get('dateSortie')
                dateRetour = request.POST.get('dateRetour')
                success = consultation.modifier_consultation(
                    id_exemplaire=id_exemplaire,
                    id_ouvrage=id_ouvrage,
                    id_bibliothecaire=id_bibliothecaire,
                    dateSortie=dateSortie,
                    dateRetour=dateRetour
                )
                if success:
                    messages.success(request, 'Consultation modifiée avec succès.')
                    return JsonResponse({'message': 'Consultation modifiée avec succès.'}, status=200)
                else:
                    messages.error(request, 'Impossible de modifier la consultation.')
                    return JsonResponse({'error': 'Impossible de modifier la consultation.'}, status=500)
            except Consulter.DoesNotExist:
                messages.error(request, 'Consultation non trouvée.')
                return JsonResponse({'error': 'Consultation non trouvée.'}, status=404)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification de la consultation.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode incorrecte.')
            return JsonResponse({'error': 'Méthode incorrecte.'}, status=405)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error':"Voun n'êtes pas autorisé à accéder à cette page."},status=403)
        


def supprimer_consultation(request, id_consultation):
    if is_bibliothecaire(request):
        if request.method == 'DELETE':
            try:
                consultation = Consulter.objects.get(id_consultation=id_consultation)
                done = Consulter.supprimer_consultation(consultation.id_consultation)
                if done:
                    messages.success(request, 'Consultation supprimée avec succès.')
                    return JsonResponse({'message': 'Consultation supprimée avec succès.'}, status=200)
                else:
                    messages.error(request, 'Échec lors de la suppression de la consultation.')
                    return JsonResponse({'error': 'Échec lors de la suppression de la consultation.'}, status=500)
            except Consulter.DoesNotExist:
                messages.error(request, 'Consultation non trouvée.')
                return JsonResponse({'error': 'Consultation non trouvée.'}, status=404)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression de la consultation.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


def historique(request):
    if is_adminSup(request):
        try:
            history_entries = LogEntry.objects.all()
            paginator = Paginator(history_entries, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'historique.html', {'page_obj': page_obj})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération de l'historique.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


def consulter(request):
    if is_bibliothecaire(request):
        id_ouvrage = request.POST.get('isbn')
        user_email = request.POST.get('user_email')

        if not (id_ouvrage and user_email):
            messages.error(request, 'Tous les champs sont requis.')
            return JsonResponse({'error': 'Tous les champs sont requis.'}, status=400)

        try:
            success, message = Consulter.consulter(id_ouvrage=id_ouvrage, id_bibliothecaire=request.user.email, id_utilisateur=user_email)
            if success:
                messages.success(request, message)
                return JsonResponse({'message': message}, status=200)
            else:
                messages.error(request, message)
                return JsonResponse({'error': message}, status=400)
        except Ouvrage.DoesNotExist:
            messages.error(request, "L'ouvrage n'existe pas.")
            return JsonResponse({'error': "L'ouvrage n'existe pas."}, status=404)
        except Personne.DoesNotExist:
            messages.error(request, "La Personne n'existe pas.")
            return JsonResponse({'error': "La personne n'existe pas."}, status=404)
        
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la consultation.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


def modify_adminsup(request):
    if is_adminSup(request):
        try:
            adminsup_id = request.POST.get('id') 
            adminsup = Personne.objects.get(id=adminsup_id)
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            
            # Check if email exists for another user
            user = Personne.objects.get(email=adminsup.email)
            exists = Personne.objects.filter(email=email).exclude(id=user.id).exists()
            if exists:
                messages.error(request, "L'email est déjà utilisé.")
                return redirect(request.META.get('HTTP_REFERER'))  # Redirect back to the same page
            
            password = request.POST.get('password')
            adminsup.nom = nom
            adminsup.prenom = prenom
            adminsup.telephone = telephone
            adminsup.email = email
            if password:
                adminsup.set_password(password)
            adminsup.save()

            messages.success(request, 'Admin sup modifié avec succès.')
            return redirect(request.META.get('HTTP_REFERER'))  
        
        except Personne.DoesNotExist:
            messages.error(request, "L'admin sup n'existe pas.")
        except DatabaseError as e:
            messages.error(request, f"Une erreur est survenue lors de la modification de l'admin sup : {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER'))  
    
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect(request.META.get('HTTP_REFERER')) 
    

@login_required
def AdminSupsView(request):
    if is_adminSup(request):
        try:
            admin_sup = Personne.objects.filter(role="ADMINSUP")
            paginator = Paginator(admin_sup, 10)

            page_number = request.GET.get('page')
            admin_sups = paginator.get_page(page_number)
            return render(request, 'adminsup.html', {'adminsups': admin_sups})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des administrateurs.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def ajouter_adminsup(request):
    if is_adminSup(request):
        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            password = request.POST.get('password')

            try:
                if Personne.objects.filter(email=email).exists():
                    messages.error(request, "L'email est déjà utilisé.")
                    return JsonResponse({'error': "L'email est déjà utilisé."}, status=400)

                adminsup = Personne(nom=nom, prenom=prenom, telephone=telephone, email=email, role="ADMINSUP")
                adminsup.set_password(password)
                adminsup.is_staff = True
                adminsup.save()

                messages.success(request, "Admin sup ajouté avec succès.")
                return JsonResponse({'message': 'Admin sup ajouté avec succès.'}, status=200)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de l'ajout de l'admin sup.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@method_decorator(login_required, name='dispatch')
class DeleteAdminSupView(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, id):
        if is_adminSup(request):
            try:
                adminsup = Personne.objects.get(id=id)
                adminsup.delete()
                messages.success(request, 'Admin supprimé avec succès.')
                return JsonResponse({'message': 'Admin supprimé avec succès.'}, status=200)
            except Personne.DoesNotExist:
                messages.error(request, "L'admin sup n'existe pas.")
                return JsonResponse({'error': "L'admin sup n'existe pas."}, status=404)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la suppression de l'admin sup.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
            return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def utilisateurs(request):
    if is_Staff(request):
        try:
            utilisateurs = Personne.objects.filter(role='UTILISATEUR')
            paginator = Paginator(utilisateurs, 10)

            page_number = request.GET.get('page')
            utilisateurs = paginator.get_page(page_number)
            return render(request, 'liste_utilisateurs.html', {'utilisateurs': utilisateurs})
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la récupération des utilisateurs.")
            return redirect('home')
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def supprimer_utilisateur(request, id):
    if is_Staff(request):
        try:
            utilisateur = Personne.objects.get(id=id, role='UTILISATEUR')
            utilisateur.delete()
            messages.success(request, 'Utilisateur supprimé avec succès.')
            return JsonResponse({'message': 'Utilisateur supprimé avec succès.'}, status=200)
        except Personne.DoesNotExist:
            messages.error(request, "L'utilisateur n'existe pas.")
            return JsonResponse({'error': "L'utilisateur n'existe pas."}, status=404)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors de la suppression de l'utilisateur.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def modifier_utilisateur(request):
    if is_Staff(request):
        if request.method == 'POST':
            try:
                utilisateur_id = request.POST.get('id')
                utilisateur = Personne.objects.get(id=utilisateur_id)

                nom = request.POST.get('nom')
                prenom = request.POST.get('prenom')
                telephone = request.POST.get('telephone')
                email = request.POST.get('email')
                password = request.POST.get('password')

                if Personne.objects.filter(email=email).exclude(id=utilisateur.id).exists():
                    messages.error(request, "L'email est déjà utilisé.")
                    return JsonResponse({'error': "L'email est déjà utilisé."}, status=400)

                utilisateur.nom = nom
                utilisateur.prenom = prenom
                utilisateur.telephone = telephone
                utilisateur.email = email

                if password:
                    utilisateur.set_password(password)

                utilisateur.save()
                messages.success(request, 'Utilisateur modifié avec succès.')
                return JsonResponse({'message': 'Utilisateur modifié avec succès.'}, status=200)
            except Personne.DoesNotExist:
                messages.error(request, "L'utilisateur n'existe pas.")
                return JsonResponse({'error': "L'utilisateur n'existe pas."}, status=404)
            except DatabaseError as e:
                messages.error(request, "Une erreur est survenue lors de la modification de l'utilisateur.")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def bannir_utilisateur(request, id):
    if is_Staff(request):
        try:
            utilisateur = Personne.objects.get(id=id, role='UTILISATEUR')
            utilisateur.bannir()
            messages.success(request, 'Utilisateur banni avec succès.')
            return JsonResponse({'message': 'Utilisateur banni avec succès.'}, status=200)
        except Personne.DoesNotExist:
            messages.error(request, "L'utilisateur n'existe pas.")
            return JsonResponse({'error': "L'utilisateur n'existe pas."}, status=404)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors du bannissement de l'utilisateur.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)


@login_required
def debannir_utilisateur(request, id):
    if is_Staff(request):
        try:
            utilisateur = Personne.objects.get(id=id, role='UTILISATEUR')
            utilisateur.debannir()
            messages.success(request, 'Utilisateur débanni avec succès.')
            return JsonResponse({'message': 'Utilisateur débanni avec succès.'}, status=200)
        except Personne.DoesNotExist:
            messages.error(request, "L'utilisateur n'existe pas.")
            return JsonResponse({'error': "L'utilisateur n'existe pas."}, status=404)
        except DatabaseError as e:
            messages.error(request, "Une erreur est survenue lors du débannissement de l'utilisateur.")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=403)

#------------------------------------------------COMMUN--------------------------------------------------
def index(request):
    try:
        ouvrages = Ouvrage.objects.all()
        categories = Categorie.objects.all()
        current_tab = 'home'
        if is_staff_no_auth(request):
            return render_admin(request, ouvrages, categories, current_tab)
        else:
            return render_user(request, ouvrages, categories, current_tab)
    except DatabaseError as e:
        messages.error(request, "Une erreur est survenue lors de la récupération des données.")
        return redirect('home')


@login_required
def render_admin(request, ouvrages, categories, current_tab):
    return render(request, 'admin_dash.html', {
        'ouvrages': ouvrages,
        'categories': categories,
        'current_tab': current_tab
    })


def render_user(request, ouvrages, categories, current_tab):
    return render(request, 'accueil.html', {
        'ouvrages': ouvrages,
        'categories': categories,
        'current_tab': current_tab
    })



#-----------------------------------COTE UTILISATEUR----------------------------------------------- 

def accieul(request):
     return render(request,"base.html",context={})







# def search(request):
#     if request.method == 'GET':
#         adresse_ip = request.META.get('REMOTE_ADDR')
      
        

        
#         try:
#             # Retrieve GET parameters
#             query = request.GET.get('query')  
#             ouvrage_search = request.GET.get("ouvrage")
#             exemplaire_search = request.GET.get("exemplaire")
#             categorie_search = request.GET.get("categorie")
#             ouvrages = Ouvrage.objects.all()  # Start with all objects
#             categories = Categorie.objects.all()
            
#             if categorie_search == 'tous_categories':
#                 categorie_search = None  # Remove category filter
#             if ouvrage_search == 'tous_ouvrages':
#                 ouvrage_search = None  # Remove ouvrage filter
                
#             if exemplaire_search:
#                  ouvrages = ouvrages.filter(titre__icontains=exemplaire_search) | ouvrages.filter(auteur__icontains=exemplaire_search)
#             else:
#                 # If exemplaire is not provided, apply other filters
#                 if ouvrage_search:
#                     ouvrages = ouvrages.filter(type=ouvrage_search)
#                 if categorie_search:
#                     ouvrages = ouvrages.filter(categorie=categorie_search)
                    
#             print(ouvrages)
            
#         except ValueError as e:
#             print(e)
#             messages.error(request, "Le type de recherche n'est pas compatible avec les champs de la classe. Vérifiez le critère de Rechercher.")
#             return render(request, 'accueil.html', {})
     
#         # Pass the queryset and categories to the template
#         return render(request, 'accueil.html', {'ouvrages': ouvrages, 'categories': categories})
#     else:
#         # If the request method is not GET, render accueil.html without any data
#         return render(request, 'accueil.html', {})

def search(request):
    ouvrages = Ouvrage.objects.all()  # Récupérer tous les ouvrages par défaut

    # Filtrer les ouvrages en fonction des paramètres de recherche
    ouvrage_type = request.GET.get('ouvrage')
    categorie = request.GET.get('categorie')
    exemplaire = request.GET.get('exemplaire')

    if ouvrage_type and ouvrage_type != 'tous_ouvrages':
        ouvrages = ouvrages.filter(type=ouvrage_type)
    
    if categorie and categorie != 'tous_categories':
        ouvrages = ouvrages.filter(categorie=categorie)
    
    if exemplaire:
        ouvrages = ouvrages.filter(titre__icontains=exemplaire)

    context = {
        'ouvrages': ouvrages,
        # Passer d'autres contextes nécessaires comme les catégories, etc.
    }
    return render(request, 'accueil.html', context)

class LoginView(View):
    

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'login.html', {})
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.is_verified:
                    login(request, user)
                    messages.success(request, 'Vous vous êtes connecté avec succès.')
                    return redirect('home')
                else:
                    messages.error(request, 'Votre compte n\'est pas activé. Veuillez vérifier votre email.')
            else:
                messages.error(request, 'Email ou mot de passe invalide.')
        
        return render(request, 'login.html', {})




@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_user(request):
    request.session.flush()
    request.session.set_expiry(0)
    logout(request)
    messages.success(request, "Vous vous êtes déconnecté.")
    response = redirect('login_user')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return redirect('home')


def apropos(request):
    current_tab="apropos"
    return render(request,'apropos.html',{
        'current_tab':current_tab
    })


def contacteznous(request):
     current_tab="contact"
     return render(request,'contacteznous.html',{
          'current_tab':current_tab
     })
 
 
 
 
def afficher_ouvrage(request,foo):
    try:
        ouvrage=Ouvrage.objects.get(ISBN=foo)
        print(ouvrage)
        if is_staff_no_auth(request):
            return render_admin_ouvrage(request, ouvrage)
        else:
            return render_user_ouvrage(request, ouvrage)
    except DatabaseError as e:
        messages.error(request, "Une erreur est survenue lors de la récupération des données.")
        return redirect('home')



@login_required
def render_admin_ouvrage(request, ouvrage):
        if is_Staff(request) :
             return render(request,'afficher_ouvrage_staff.html',{
            'ouvrage':ouvrage
        })
        else :
            return render_user_ouvrage(request,ouvrage)


def render_user_ouvrage(request, ouvrage):
    return render(request,'afficher_ouvrage.html',{
            'ouvrage':ouvrage
        })
    



# def register_user(request):
#     form = SignUpForm()
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             #user = form.save()
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password1']
#             email=form.cleaned_data['email']
#             nom=form.cleaned_data['nom']
#             prenom=form.cleaned_data['prenom']
#             telephone=form.cleaned_data['telephone']
#             image_data = request.POST.get('image')  
#             role=request.POST.get('role')
#             #email, username, password, nom, prenom, telephone,role='UTILISATEUR',**extra_fields):
#             if role == 'UTILISATEUR':
#                 user = Utilisateur.objects.create_user(email,username,password,nom,prenom,telephone,'UTILISATEUR')
#             elif role == 'BIBLIOTHECAIRE':
#                 user = Bibliothecaire.objects.create_user(email,username,password,nom,prenom,telephone,'BIBLIOTHECAIRE')
#             elif role == 'ADMINSUP':
#                 user = AdminSup.objects.create_superuser(email,username,password,nom,prenom,telephone,'ADMINSUP')
        
#             user.save()
#             user = authenticate(request, email=email, password=password)
#             print(user)
#             if user is not None:
                
#                 login(request, user)
#                 messages.success(request, "Vous vous êtes inscrit avec succès.")
#                 return redirect('home') 
#             else:
#                 messages.error(request, "Erreur dans l'authentification")
#                 return redirect('home') 
#                 #messages.error(request, "Échec de l'authentification de l'utilisateur après l'inscription.")
#         else:
            
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"Erreur dans {field}: {error}")
#     return render(request, 'register.html', {'form': form})

class RegisterView(View):
    form_class = SignUpForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            email = form.cleaned_data['email']
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            telephone = form.cleaned_data['telephone']
            image_data = request.POST.get('image')
            role = 'UTILISATEUR'

            user = Personne.objects.create_user(
                email=email,
                password=password,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                role=role,
                image_data=image_data
            )
            user.is_active = False  # Désactiver l'utilisateur jusqu'à l'activation
            user.save()

            # Envoyer l'e-mail d'activation
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Activation de votre compte'
            message = render_to_string('activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, 'Vous avez créé un compte. Activez votre compte depuis votre email pour pouvoir y accéder.')
            return redirect('home')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")

        return render(request, 'register.html', {'form': form})
    

class RegisterAdminView(View):
    form_class = SignUpForm

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            telephone = form.cleaned_data['telephone']
            image_data = request.POST.get('image')
            user = PersonneManager.create_superuser(PersonneManager, email=email,telephone=telephone,image_data=image_data, nom=nom, prenom=prenom, password=password)
            if user is not None:
                messages.success(request, "Administrateur ajouté avec succès.")
                
            else:
                messages.error(request, "Erchec lors de l'ajout de l'administrateur : ",nom," ",prenom)
                
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")


    
class GererReservations(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        try:
            reservations=Reservation.objects.filter(id_utilisateur=request.user.id)
            return render(request,'gerer_reservations.html',{
                "reservations":reservations
            })
        except Exception as e:
            messages.error(request,e)
            return render(request,"accueil.html")

class AnnulerReservations(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.user.is_authenticated:
                ouvrage_isbn = request.POST.get('ouvrage_isbn')
                try:
                    ouvrage = Ouvrage.objects.get(ISBN=ouvrage_isbn)
                    ouvrage.num_exmp_dispo+=1
                    ouvrage.save()
                    # Assuming there can be multiple reservations for the same book
                    reservations = Reservation.objects.filter(ouvrage=ouvrage)
                    if reservations.exists():
                        # Delete all reservations for the given book
                        reservations.delete()
                        messages.success(request, "Les réservations ont été annulées avec succès.")
                        return redirect("gerer")
                    else:
                        messages.error(request, "Aucune réservation trouvée pour cet ouvrage.")
                except Ouvrage.DoesNotExist:
                    messages.error(request, "L'ouvrage n'a pas été trouvé.")
            else:
                messages.error(request, "Vous devez vous connecter d'abord.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reversed('home')))



class GererEmptunts(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        emprunts=Emprunter.objects.filter(utilisateur=request.user)
        return render(request, 'emprunts_user.html', {
            'emprunts':emprunts
        })
    
    
class SignalerPerte(View):
        
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
            if request.POST.get('action') == 'post':
                
                exemplaire_id = int(request.POST.get('exemplaire_id'))
                print(exemplaire_id)
                try:
                    exemplaire=Exemplaire.objects.get(id_exemplaire=exemplaire_id)
                    user=Personne.objects.get(id=request.user.id)
                    if user.signaler_perte(exemplaire):
                        messages.warning(request,"Votre Exemplaire est signlé perdu, Vous devez passer chez le bibliothécaire")
                        return redirect('home')
                    else:
                        messages.error(request,"Un prblème lore de signalisation de Perte")
                        return redirect('home')
                            
                except Ouvrage.DoesNotExist:
                    messages.error(request, 'L\'exemplaire spécifié n\'existe pas.')
                    return redirect('home')

class SignalerDeterioration(View):
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
            if request.POST.get('action') == 'post':
                print(request.POST.get('exemplaire_id'),type(request.POST.get('exemplaire_id')))
                exemplaire_id = int(request.POST.get('exemplaire_id'))
                try:
                    exemplaire=Exemplaire.objects.get(id_exemplaire =exemplaire_id)
                    user=Personne.objects.get(id=request.user.id)
                    if user.signaler_deterioration(exemplaire):
                        messages.warning(request,"Votre Exemplaire est signlé détérioré , Vous devez passer chez le bibliothécaire")
                        
                        return redirect('home')
                    else:
                        messages.error(request,"Un prblème lore de signalisation de détériration ")
                        return redirect('home')
                            
                except Ouvrage.DoesNotExist:
                    messages.error(request, 'L\'exemplaire spécifié n\'existe pas.')
                    return redirect('home')
                
class UpdateUser(View):
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated :
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = Personne.objects.get(email=request.user.email)
            
            user_form = UpdateUserForm(instance=current_user)
            if is_Staff(request) :
                return render(request, "update_profile_staff.html", {'user_form': user_form})
            else :
                return render(request, "update_profile.html", {'user_form': user_form})
        else:
            messages.error(request, "Vous devez vous authentifier ")
            return redirect('home')
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = Personne.objects.get(email=request.user.email)
            
            user_form = UpdateUserForm(request.POST or None, instance=current_user)
            if user_form.is_valid():
                user_form.save()
                login(request, current_user)
                messages.success(request, "Profile est mis à jour")
                return redirect('home')
            if is_Staff(request) :
                return render(request, "update_profile_staff.html", {'user_form': user_form})
            else :
                return render(request, "update_profile.html", {'user_form': user_form})
        else:
            messages.error(request, "Vous devez vous authentifier ")
            return redirect('home')
        
class UpdatePswd(View):
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated :
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = Personne.objects.get(email=request.user.email)
            
            user_form = ChangePasswordForm(user=current_user)
            if is_Staff(request) :
                return render(request, "update_pswd_staff.html", {'form': user_form})
            else :
                return render(request, "update_pswd.html", {'form': user_form})
        else:
            messages.error(request, "Vous devez vous authentifier ")
            return redirect('home')
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user=request.user
            if request.method =='POST':
                form=ChangePasswordForm(current_user,request.POST)
                
                # if the form valid
                
                if form.is_valid():
                    form.save()
                    messages.success(request,"Votre mot de passe est changé avec succès ")
                    login(request,current_user)
                    return redirect('home')
                else:
                    for error in form.errors.items:
                        messages.error(request,error)
                        return redirect('home')
            else:
                form=ChangePasswordForm(current_user)
                return render(request,'update_pswd.html',{
                    'form':form
                })
        else:
            messages.error(request,"Vous devez vous connecter")
            return redirect('home')
        
@login_required
@require_POST
def prolonger_date_retour(request):
    id_emprunt = request.POST.get('id_emprunt')
    new_return_date_str = request.POST.get('new_return_date')
    
    emprunt = Emprunter.objects.get(id_emprunt=id_emprunt)
    max_allowed_return_date = (emprunt.date_retour + timedelta(days=6)).date()
    new_return_date = datetime.strptime(new_return_date_str, '%Y-%m-%d').date()
    
    if new_return_date > max_allowed_return_date:
        messages.warning(request,"Vous ne pouvez pas prolonger l'emprunt plus de 6 jours")
        return JsonResponse({'message': "Vous ne pouvez pas prolonger l'emprunt plus de 6 jours"})
    
    if emprunt.num_extensions>1:
        messages.warning(request,"Vous avez dépassé le nombre de prolongations autorisées")
        return JsonResponse({'message': "Vous avez dépassé le nombre de prolongations autorisées"})
    emprunt.num_extensions=emprunt.num_extensions+1
    emprunt.date_retour = new_return_date
    emprunt.save()
    
    # Create a notification for adherents
    biblios = Personne.objects.filter(role='BIBLIOTHECAIRE')
    message = f"L'utilisateur {request.user.email} a prolongé la date de retour pour l'emprunt {emprunt.id_emprunt} jusqu'au {new_return_date}"
    for biblio in biblios:
        Notification.objects.create(user=biblio, message=message)
    messages.success(request,f"La date de retour est prolongée avec succès jusqu'au {new_return_date}")
    return JsonResponse({'message': f"La date de retour est prolongée avec succès jusqu'au {new_return_date}"})




@login_required
def notifications_view(request):
    if is_bibliothecaire :
        notifications = Notification.objects.filter(read=False)
        return render(request, 'notifications.html', {'notifications': notifications})
    else:
        return redirect('home')

@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.read = True
        notification.save()
        return redirect('notifications_view')
    except Notification.DoesNotExist:
        messages.error(request, "Notification n'existe pas ou vous n'avez pas d'accées")
        return redirect('notifications_view')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('notifications_view')
    

############################## RESERT PASSWORD BY EMAIL

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'forget_password_from_email.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        
        users = list(self.get_users(email))
        
        if not users:
           
            messages.error(self.request, "Aucun utilisateur trouvé avec cet email.")
            return redirect("login_user")
       
        return super().form_valid(form)

    def form_invalid(self, form):
        
        print("form is unvalid")
        return redirect("login_user")

    def get_users(self, email):
        UserModel = get_user_model()
        active_users = UserModel._default_manager.filter(
            email__iexact=email,
            is_active=True,
        )
        return (u for u in active_users if u.has_usable_password())
    
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_verified = True
        user.is_active = True
        user.save()
        messages.success(request, 'Vous avez activé votre compte. Vous pouvez maintenant vous connecter.')
        return redirect('login_user')
    else:
        messages.error(request, 'Le lien d\'activation est invalide !')
        return redirect('register')
    
def send_notification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Save the notification
        bibliothecaires = Personne.objects.filter(role='BIBLIOTHECAIRE')
        for biblio in bibliothecaires:
            # Save notification
            notification_message = f"{message} d'utilisateur {email}"
            notification = Notification(user=biblio, message=notification_message)
            notification.save()
            
            # Send email
            subject = "Contact de Bibliotech "+ email
            email_message = render_to_string('notification_email.html', {
                'user': biblio,
                'message': notification_message
            })
            send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [biblio.email])

        messages.success(request,"Votre message et envoyé avec succés")
        return redirect('contacteznous')  
    
    
    