from django.shortcuts import render,redirect
from biblio_app.models import *
from .cart import Cart
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_variables
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta

def cart_add(request):
    cart=Cart(request)
    #test for post
    if request.POST.get('action')=='post':
        ouvrage_id=request.POST.get('ouvrage_id')
      
        ouvrage = get_object_or_404(Ouvrage, ISBN=ouvrage_id)
        if len(cart.cart) > 3:
            messages.error(request, 'Vous ne pouvez pas ajouter plus de 3 exemplaires.')
            return JsonResponse({})

        
        
            cart_quantity=cart.__len__()
            
            
            #response= JsonResponse({'product_id':product.id,'product Name':product.name})
            response= JsonResponse({
                'qty':cart_quantity,
            })
        
        
            return response
        
        if ouvrage.num_exemplaire > 0:
            
            cart.add(ouvrage=ouvrage)
            messages.success(request,'L\'exemplaire est ajouté avec succès')
            #get the quantity
        
            cart_quantity=cart.__len__()
            
            
            #response= JsonResponse({'product_id':product.id,'product Name':product.name})
            response= JsonResponse({
                'qty':cart_quantity,
            })
        
        
            return response
        else:
            messages.error(request,'L\'exemplaire est Hors Stock')
            cart_quantity=cart.__len__()
            response= JsonResponse({
                'qty':cart_quantity,
            })
            return response
        
    
    

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        ouvrage_isbn= request.POST.get('ouvrage_isbn')
        cart.delete(ouvrage_isbn=ouvrage_isbn)
        response = JsonResponse({'ouvrage_isbn': ouvrage_isbn})
        messages.success(request,"l\'exemplaire est enlevé avec succès")
        return response
    
    
def deleteAllfromBin(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        cart.deleteAll()
        response = JsonResponse({})
        messages.success(request,"l\'exemplaire est enlevé avec succès")
        return response
   
   
   
 

@login_required
def reserver_tous(request):
    if request.user.is_authenticated:
        cart = Cart(request)
        ouvrages = cart.get_exemplaires()
        date_debut_emprunt_tous = request.POST.get("date_debut_emprunt_tous")
        
        if len(cart)>3:
            messages.error(request, "Vous ne pouvez pas séléctionnez plus  que 3 ouvrages pour la réservation")
            return JsonResponse({'success': False, 'message': 'len invalide'}, status=500)
        if request.user.is_authenticated:
            if date_debut_emprunt_tous:
                date_debut_emprunt_tous = timezone.datetime.strptime(date_debut_emprunt_tous, "%Y-%m-%d").date()
                today_date = timezone.now().date()
                
                # Check if the date_debut_emprunt_tous is within 3 days from today
                if date_debut_emprunt_tous <= today_date + timedelta(days=3) or today_date>date_debut_emprunt_tous:
                    for ouvrage in ouvrages:
                        utilisateur = Personne.objects.get(id=request.user.id)
                        if utilisateur.est_banni():
                            messages.error(request,'Vous etes  banni de reserver les exemplaires , contactrez le bibliothecaire')
                            return JsonResponse({'success': False, 'message': 'Utilisateur banni.'})
                        ouvrage.num_exmp_dispo=ouvrage.num_exmp_dispo-1
                        ouvrage.save()
                        reservation = Reservation(ouvrage=ouvrage, 
                                                date_reservation=today_date, 
                                                id_utilisateur=utilisateur, 
                                                date_emprunt=date_debut_emprunt_tous)
                        reservation.save()
                        cart.delete(ouvrage.ISBN)
                    
                    messages.success(request, "Tous les ouvrages dans votre liste sont réservés avec succès, Vous devez passer le "+str(today_date)+" pour les recuperer")
                    return JsonResponse({'success': True, 'message': 'Reservation fait'}, status=200)
                else:
                    messages.error(request, "La date de début d'emprunt ne peut pas être plus de 3 jours à partir d'aujourd'hui.")
                    return JsonResponse({'success': False, 'message': 'Date Invalide'}, status=500)
            else:
                messages.error(request, "La date de début d'emprunt est requise.")
                return JsonResponse({'success': False, 'message': 'Date requise'}, status=500)
        else:
            messages.error(request, "Vous devez vous authentifier d'abord.")
            return redirect('login')
    else :
        messages.error(request, "Vous devez vous authentifier d'abord.")
        return redirect('login_user')
    
    
@login_required
def reserver_tous(request):
    cart = Cart(request)
    ouvrages = cart.get_exemplaires()
    date_debut_emprunt_tous = request.POST.get("date_debut_emprunt_tous")
    
    if len(cart)>3:
        messages.error(request, "Vous ne pouvez pas séléctionnez plus  que 3 ouvrages pour la réservation")
        return JsonResponse({'success': False, 'message': 'len invalide'}, status=500)
    if request.user.is_authenticated:
        if date_debut_emprunt_tous:
            date_debut_emprunt_tous = timezone.datetime.strptime(date_debut_emprunt_tous, "%Y-%m-%d").date()
            today_date = timezone.now().date()
            
            # Check if the date_debut_emprunt_tous is within 3 days from today
            if date_debut_emprunt_tous <= today_date + timedelta(days=3) or today_date>date_debut_emprunt_tous:
                for ouvrage in ouvrages:
                    utilisateur = Personne.objects.get(id=request.user.id)
                    if utilisateur.est_banni():
                        messages.error(request,'Vous etes  banni de reserver les exemplaires , contactrez le bibliothecaire')
                        return JsonResponse({'success': False, 'message': 'Utilisateur banni.'})
                    ouvrage.num_exmp_dispo=ouvrage.num_exmp_dispo-1
                    ouvrage.save()
                    reservation = Reservation(ouvrage=ouvrage, 
                                              date_reservation=today_date, 
                                              id_utilisateur=utilisateur, 
                                              date_emprunt=date_debut_emprunt_tous)
                    reservation.save()
                    cart.delete(ouvrage.ISBN)
                
                messages.success(request, "Tous les ouvrages dans votre liste sont réservés avec succès, Vous devez passer le "+str(today_date)+" pour les recuperer")
                return JsonResponse({'success': True, 'message': 'Reservation fait'}, status=200)
            else:
                messages.error(request, "La date de début d'emprunt ne peut pas être plus de 3 jours à partir d'aujourd'hui.")
                return JsonResponse({'success': False, 'message': 'Date Invalide'}, status=500)
        else:
            messages.error(request, "La date de début d'emprunt est requise.")
            return JsonResponse({'success': False, 'message': 'Date requise'}, status=500)
    else:
        messages.error(request, "Vous devez vous authentifier d'abord.")
        return redirect('login_user')
    
    
@login_required
def reserver_exemplaire(request):
    cart = Cart(request)
    ouvrage_isbn = request.POST.get('ouvrage_isbn')
    date_debut_emprunt = request.POST.get("date_debut_emprunt")

    # Convert date_debut_emprunt to a date object
    try:
        date_debut_emprunt = datetime.strptime(date_debut_emprunt, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Date de début d'emprunt invalide.")
        return JsonResponse({'status': 'error', 'message': 'Date de début d\'emprunt invalide.'})

    # Check if date_debut_emprunt is not more than 3 days from today
    today_date = timezone.now().date()
    if date_debut_emprunt > today_date + timedelta(days=3) or today_date>date_debut_emprunt:
        messages.error(request, "La date de début d'emprunt ne peut pas être plus de 3 jours à partir d'aujourd'hui.")
        return JsonResponse({'status': 'error', 'message': 'Date de début d\'emprunt trop éloignée.'})
    
        

    ouvrage = get_object_or_404(Ouvrage, ISBN=ouvrage_isbn)
    if ouvrage.num_exmp_dispo<2:
        messages.error(request, "Désolé, Vous ne pouvez pas faire une reservation, Veuillez le consulter sur place")
        return JsonResponse({'status': 'error', 'message': 'consultation instead'})
    if ouvrage.num_exmp_dispo > 0:
        utilisateur_instance = Personne.objects.get(id=request.user.id)
        if utilisateur_instance.role=='UTILISATEUR':

            if utilisateur_instance.est_banni():
                            messages.error(request,'Vous etes  banni de reserver les exemplaires , contactrez le bibliothecaire')
                            return JsonResponse({'success': False, 'message': 'Utilisateur banni.'})
            active_reservations = Reservation.objects.filter(id_utilisateur=utilisateur_instance)
            if len(active_reservations) > 3:
                messages.error(request, "Vous ne pouvez pas réserver plus de trois ouvrages.")
                return JsonResponse({'status': 'error', 'message': 'Plus de trois'})
            else:
                ouvrage.num_exmp_dispo=ouvrage.num_exmp_dispo-1
                ouvrage.save()
                
                
                reservation = Reservation(
                    ouvrage=ouvrage,
                    date_reservation=today_date,
                    date_emprunt=date_debut_emprunt,
                    id_utilisateur=utilisateur_instance
                )
                print(reservation.date_emprunt)
                print(reservation.date_reservation)
                reservation.save()
                cart.delete(ouvrage.ISBN)
                messages.success(request, "Votre réservation a été effectuée avec succès. Vous devez passer à la bibliothèque le "+ str(date_debut_emprunt)+ " pour récupérer votre exemplaire.")
                return JsonResponse({'status': 'success'})
    else:
        messages.error(request, "Désolé, tous les exemplaires de ce livre sont actuellement empruntés.")
        return JsonResponse({'status': 'error', 'message': 'Tous les exemplaires empruntés'})
        

#Gestion des emprunts
def is_Staff(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'BIBLIOTHECAIRE' :
        return True
    else:
        return False
    
@login_required
def emprunter(request):
    cart = Cart(request)
    authorized = is_Staff(request)
    if authorized:
        if request.method == 'POST':
            id_ouvrage = request.POST.get('isbn')
            user_email = request.POST.get('user_email')
            # Retrieve the user ID based on the email
            try:
                utilisateur = Personne.objects.get(email=user_email, role='UTILISATEUR')
            except Personne.DoesNotExist:
                messages.error(request,'Utilisateur introuvable.')
                return JsonResponse({'success': False, 'message': 'Utilisateur introuvable.'}, status=400)
            success,consulter, message = Emprunter.emprunter(id_ouvrage=id_ouvrage, id_bibliothecaire=request.user.email, id_utilisateur=utilisateur.email)
            if success:
                cart.delete(id_ouvrage)
                print(id_ouvrage)
                messages.success(request,message)
                return JsonResponse({'success': True, 'message': message}, status=200)
            elif consulter == 1:
                return JsonResponse({'consulter': message}, status=400)
                
            else:
                messages.error(request,message)
                return JsonResponse({'success': False, 'message': message}, status=400)
        else:
            messages.error(request,'Requête invalide')
            return JsonResponse({'success': False, 'message': 'Utilisateur introuvable.'}, status=400)
    else :
        return JsonResponse({'success': False, 'message': 'Requête invalide.'}, status=500)
    

@login_required
@require_POST
def emprunter_tous(request):
    cart = Cart(request)
    authorized = is_Staff(request)
    if authorized:
        cart = Cart(request)
        ouvrages = cart.get_exemplaires()
        if len(ouvrages)>0 and len(ouvrages)<4 :
            if request.method == 'POST':
                user_email = request.POST.get('user_email')
                print(user_email)
                # Retrieve the user ID based on the email
                try:
                    utilisateur = Personne.objects.get(email=user_email, role='UTILISATEUR')
                except Personne.DoesNotExist:
                    messages.error(request,'Utilisateur introuvable.')
                    return JsonResponse({'success': False, 'message': 'Utilisateur introuvable.'}, status=400)
                
                success_count = 0
                failure_count = 0
                failure_messages = []

                # Attempt to borrow each ouvrage
                for ouvrage in ouvrages:
                    success,consulter,message = Emprunter.emprunter(id_ouvrage=ouvrage.ISBN, id_bibliothecaire=request.user.email, id_utilisateur=utilisateur.email)
                    if success:
                        cart.delete(ouvrage.ISBN)
                        success_count += 1
                        print(ouvrage)
                        cart.delete(ouvrage)
                    else:
                        failure_count += 1
                        failure_messages.append(message)

                # Generate the overall response message
                if failure_count == 0:
                    messages.success(request,f'Tous les emprunts ont été effectués avec succès ({success_count} sur {len(ouvrages)}).')
                   
                    return JsonResponse({'success': False, 'message' :f'Tous les emprunts ont été effectués avec succès ({success_count} sur {len(ouvrages)}).'}, status=200)
                else:
                    messages.error(request,f'{failure_count} emprunt(s) ont échoué. Détails : {", ".join(failure_messages)}')
                 
                    return JsonResponse({'success': False, 'message' :f'{failure_count} emprunt(s) ont échoué. Détails : ", ".{failure_messages}'}, status=400)

            else:
                messages.error(request,'Invalid request method')
                return JsonResponse({'success': False, 'message' : 'Invalid request method'}, status=400)
        else :
            messages.error(request,'Vous ne pouvez faire qu\'une consultation sur place' )
            return JsonResponse({'success': False, 'message' : 'Choisissez 1 à 3 pour affectuer l\'emprunt' }, status=400)
    else :
         return JsonResponse({'success': False, 'message' : 'Vous n\'êtes pas autorisé à effectuer cette requête' }, status=500)
    


def is_staff_no_auth(request):
    if request.user.is_authenticated and (request.user.role == 'BIBLIOTHECAIRE'):
        return True
    else:
        return False 
    
def cart_summary(request):
    cart=Cart(request)
    cart_exemplaires=cart.get_exemplaires()
    disable = False
    for ex in cart_exemplaires:
        if ex.num_exmp_dispo <= 1:
            disable = True
            break
    
    if is_staff_no_auth(request):
        return render_admin(request,cart_exemplaires=cart_exemplaires,disable=disable)
    else:
        return render_user(request,cart_exemplaires)


@login_required
def render_admin(request,cart_exemplaires,disable):
    return render(request,'cart_summary_staff.html',{
        'cart_exemplaires':cart_exemplaires,
        "disable" : disable
        })


def render_user(request,cart_exemplaires):
        return render(request,'cart_summary.html',{
            'cart_exemplaires':cart_exemplaires,
        })



def consulter(request):
    if is_Staff(request):
        cart = Cart(request)
        id_ouvrage = request.POST.get('isbn')
        user_email = request.POST.get('user_email')

        if not (id_ouvrage and user_email):
            messages.error(request,'Tous les champs sont requis.')
            return JsonResponse({ 'error': 'Tous les champs sont requis.'}, status=400 )
        
        try:
            success, message = Consulter.consulter(id_ouvrage=id_ouvrage, id_bibliothecaire=request.user.email, id_utilisateur=user_email)
            if success :
                cart.delete(id_ouvrage)
                messages.success(request,message)
                return JsonResponse({'message': message}, status=200)
            else :
                messages.error(request,message)
                return JsonResponse({'error': message}, status=400)
        except Ouvrage.DoesNotExist:
            messages.error(request,"L'ouvrage n'existe pas.")
            return JsonResponse({'error': "L'ouvrage n'existe pas."}, status=500)
        except Personne.DoesNotExist:
            messages.error(request,"Cet utilisateur n'existe pas.")
            return JsonResponse({'error': "L'adhérent n'existe pas."}, status=500)
        except Personne.DoesNotExist:
            messages.error(request,"L'utilisateur n'existe pas.")
            return JsonResponse({'error': "L'utilisateur n'existe pas."}, status=500)
        except Exception as e:
            messages.error(request,str(e))
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)
    
    
@login_required
def modifier_reservation(request):
    date_debut_emprunt=request.POST.get('date_debut_emprunt')
    id_reservation=request.POST.get("id_reservation")
    print(date_debut_emprunt)
    cart = Cart(request)
    ouvrage_isbn = request.POST.get('ouvrage_isbn')
    date_debut_emprunt = request.POST.get("date_debut_emprunt")

    # Convert date_debut_emprunt to a date object
    try:
        date_debut_emprunt = datetime.strptime(date_debut_emprunt, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Date de début d'emprunt invalide.")
        return JsonResponse({'status': 'error', 'message': 'Date de début d\'emprunt invalide.'})

    # Check if date_debut_emprunt is not more than 3 days from today
    today_date = timezone.now().date()
    if date_debut_emprunt > today_date + timedelta(days=3):
        messages.error(request, "La date de début d'emprunt ne peut pas être plus de 3 jours à partir d'aujourd'hui.")
        return JsonResponse({'status': 'error', 'message': 'Date de début d\'emprunt trop éloignée.'})
    else:
        reservation = Reservation.objects.get(id_reservation=id_reservation)
        if reservation.modify_reservation(reservation.id_reservation,date_debut_emprunt,request.user.id):
            messages.success(request, "Votre réservation a été mofifié avec succès.")
            return JsonResponse({'status': 'success'})
        else:
            messages.error(request, "Erreur lore de modification de la réservation")
            return JsonResponse({'status': 'error'})